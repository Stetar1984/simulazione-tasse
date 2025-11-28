import streamlit as st

# Configurazione pagina
st.set_page_config(page_title="Simulazione Fiscale", layout="wide")

st.title("📊 Simulatore Fiscale: Ordinario vs Forfettario")
st.markdown("Analisi basata sui dati dell'immagine caricata")

# ==============================================================================
# 1. INPUT DATI (Pre-compilati con i valori del tuo Excel)
# ==============================================================================
with st.sidebar:
    st.header("1. Dati Economici")
    ricavi_compensi = st.number_input("Ricavi (A)", value=33616)
    costi_spese = st.number_input("Costi (B)", value=19076)
    
    st.header("2. IVA")
    iva_a_debito = st.number_input("IVA a debito (Incassata)", value=7395)
    iva_a_credito = st.number_input("IVA a credito (Acquisti)", value=2600)
    
    st.header("3. Detrazioni (Ordinario)")
    detraz_oneri = st.number_input("Detraz. oneri (Sanità, ecc.)", value=2635)
    detraz_lav_autonomo = st.number_input("Detrazione lav. aut. (Riga rossa)", value=890, help="Inserisci il valore che trovi nel tuo excel alla voce Detrazione reddito impresa")
    
    st.header("4. INPS (Fondamentale!)")
    st.info("Inserisci i valori esatti del riquadro 'Risultato Verifica' o delle colonne")
    inps_ordinario = st.number_input("Contributi Ordinario", value=3810)
    # Nota: Nell'excel il forfettario è calcolato nella colonna E (4.208) ma nel riepilogo in basso usa 6.595.
    # Imposto 6.595 per far tornare il calcolo finale di -936.
    inps_forfettario = st.number_input("Contributi Forfettario", value=6595)

    st.header("5. Parametri")
    coeff_redditivita = 67 # Fisso per parrucchieri
    aliquota_sostitutiva = 15 # 15% standard
    addizionali_totali = 186 # Valore fisso preso dal tuo excel per semplificare

# ==============================================================================
# 2. CALCOLI ESATTI (Logica Excel)
# ==============================================================================

# --- A. ORDINARIO ---
# Reddito Imponibile
reddito_operativo = ricavi_compensi - costi_spese # 14.540
imponibile_irpef = reddito_operativo - inps_ordinario # 10.730

# IRPEF Lorda (Calcolo approssimato 23%)
irpef_lorda = imponibile_irpef * 0.23 

# Totale Detrazioni
tot_detrazioni = detraz_oneri + detraz_lav_autonomo # 2635 + 890 = 3525

# IRPEF Netta (Se le detrazioni superano l'imposta, è 0)
irpef_netta = max(0, irpef_lorda - tot_detrazioni)

# Totale Tasse Ordinario (IRPEF + Addizionali)
tasse_ordinario = irpef_netta + addizionali_totali # 0 + 186 = 186

# USCITA TOTALE ORDINARIO
uscita_ord = tasse_ordinario + inps_ordinario # 186 + 3810 = 3996


# --- B. FORFETTARIO ---
# Ricavi Lordi (Colonna C)
ricavi_lordi_forf = ricavi_compensi + iva_a_debito # 41.011

# Imponibile Lordo (Colonna D)
imponibile_lordo = ricavi_lordi_forf * (coeff_redditivita / 100) # 27.477

# Imponibile Netto (D - Contributi)
# Attenzione: l'Excel usa per l'imponibile netto il valore 4.208 (colonna E in alto) 
# o il valore 6.595 (riepilogo in basso)? 
# Dal calcolo dell'imposta (3.132 che è il 15% di 20.883), si deduce che:
# 27.477 - X = 20.883 => X = 6.594 (Quindi usa l'INPS alto)
imponibile_netto = imponibile_lordo - inps_forfettario

# Imposta Sostitutiva (15%)
imposta_sostitutiva = imponibile_netto * (aliquota_sostitutiva / 100) 

# Effetto IVA (Positivo)
effetto_iva = iva_a_debito - iva_a_credito # 4795

# USCITA TOTALE FORFETTARIO (Calcolo Reale)
# Tasse + INPS - (Soldi IVA intascati)
uscita_forf = (imposta_sostitutiva + inps_forfettario) - effetto_iva

# Differenza (Ordinario - Forfettario)
differenza = uscita_ord - uscita_forf

# ==============================================================================
# 3. VISUALIZZAZIONE
# ==============================================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏛️ Regime Ordinario")
    st.write(f"Imposte Dirette: **{tasse_ordinario:,.0f} €**")
    st.write(f"Contributi INPS: **{inps_ordinario:,.0f} €**")
    st.error(f"TOTALE USCITE: {uscita_ord:,.0f} €")

with col2:
    st.subheader("✂️ Regime Forfettario")
    st.write(f"Imposta Sostitutiva: **{imposta_sostitutiva:,.0f} €**")
    st.write(f"Contributi INPS: **{inps_forfettario:,.0f} €**")
    st.success(f"Vantaggio IVA (Incassata-Persa): **-{effetto_iva:,.0f} €**")
    st.warning(f"Costro Reale (Tasse+INPS-IVA): {uscita_forf:,.0f} €")

st.markdown("---")

# Visualizzazione Risultato Finale stile Excel
st.markdown("### 🏁 RISULTATO CONFRONTO")

col_res1, col_res2, col_res3 = st.columns([1,1,1])
with col_res1:
    st.metric("Totale Imposte Diff.", f"{tasse_ordinario - imposta_sostitutiva:,.0f} €")
with col_res2:
    st.metric("Effetto IVA", f"+{effetto_iva:,.0f} €")
with col_res3:
    st.metric("Diff. Contributi", f"{inps_ordinario - inps_forfettario:,.0f} €")

st.markdown("---")

if differenza > 0:
    st.success(f"✅ CONVIENE IL FORFETTARIO di {differenza:,.0f} €")
else:
    st.error(f"❌ NON CONVIENE IL FORFETTARIO (Meglio Ordinario)")
    st.metric(label="Perdita stimata passando al forfettario", value=f"{differenza:,.0f} €")
    
    # Spiegazione matematica precisa
    st.write(f"""
    **Perché esce {differenza:,.0f} €? Ecco la matematica:**
    
    1. Nell'Ordinario spendi **{uscita_ord:,.0f} €** (tra tasse e INPS).
    2. Nel Forfettario spenderesti **{uscita_forf:,.0f} €** (considerando che l'IVA ti ripaga parte delle tasse).
    3. La differenza è **{uscita_ord:,.0f} - {uscita_forf:,.0f} = {differenza:,.0f} €**.
    """)

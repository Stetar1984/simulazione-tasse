import streamlit as st

# Configurazione pagina
st.set_page_config(page_title="Simulazione Fiscale Dettagliata", layout="wide")

st.title("📊 Simulatore Fiscale: Ordinario vs Forfettario")
st.markdown("Replicazione fedele del file Excel per Parrucchieri (ATECO 96.02.01)")

# ==============================================================================
# 1. COLONNA LATERALE - INSERIMENTO DATI (Come nel file Excel)
# ==============================================================================
with st.sidebar:
    st.header("1. Dati Attività (Vedi Colonna A e B)")
    ricavi_compensi = st.number_input("Ricavi / Compensi (A)", value=33616, step=100)
    costi_spese = st.number_input("Costi / Spese (B)", value=19076, step=100)
    
    st.header("2. Dati IVA (Fondamentali)")
    iva_a_debito = st.number_input("IVA a debito (Incassata dai clienti)", value=7395, step=50, help="L'IVA che hai aggiunto agli scontrini")
    iva_a_credito = st.number_input("IVA a credito (Sugli acquisti)", value=2600, step=50, help="L'IVA che hai pagato ai fornitori")
    
    st.header("3. Detrazioni e Addizionali (Ordinario)")
    detraz_oneri = st.number_input("Ammontare detraz. oneri (Sanità, ecc.)", value=2635, step=50)
    detraz_lav_autonomo = st.number_input("Detrazione reddito impresa/lav.aut.", value=890, step=10, help="Calcolata in base al reddito, nel tuo file è 890")
    aliq_add_regionale = st.number_input("Aliq. Add. Regionale (%)", value=1.23, step=0.01, format="%.2f")
    aliq_add_comunale = st.number_input("Aliq. Add. Comunale (%)", value=0.50, step=0.01, format="%.2f")

    st.header("4. Parametri Forfettario")
    coeff_redditivita = st.number_input("Coefficiente Redditività (%)", value=67, step=1)
    aliquota_sostitutiva = st.selectbox("Aliquota Imposta Sostitutiva", [15, 5], index=0, help="15% standard, 5% per start-up prime 5 anni")
    
    st.header("5. Opzioni INPS")
    # Qui permettiamo di scegliere se usare il calcolo automatico o forzare i numeri dell'Excel
    usa_inps_manuale = st.checkbox("Inserisci INPS manualmente (come da Excel)", value=False)
    
    if usa_inps_manuale:
        inps_ordinario = st.number_input("INPS Ordinario (Manuale)", value=3810)
        inps_forfettario = st.number_input("INPS Forfettario (Manuale)", value=6595)
    else:
        st.caption("Calcolo automatico INPS Artigiani/Comm. (Minimale + Eccedenza)")
        riduzione_inps_35 = st.checkbox("Richiedi riduzione INPS 35% (Forfettario)?", value=False)
        # Logica semplificata INPS per simulazione (Minimale 2024 approx 4400 o % su reddito)
        # Usiamo una % fissa stimata per replicare i numeri del file (circa 26% su imponibile)
        aliquota_inps_stima = 0.261 
        
        # Calcolo INPS Ordinario
        reddito_operativo = ricavi_compensi - costi_spese
        inps_ordinario = reddito_operativo * aliquota_inps_stima
        
        # Calcolo INPS Forfettario
        base_forf = (ricavi_compensi + iva_a_debito) * (coeff_redditivita / 100)
        inps_forfettario = base_forf * aliquota_inps_stima
        if riduzione_inps_35:
            inps_forfettario = inps_forfettario * 0.65

# ==============================================================================
# 2. LOGICA DI CALCOLO (Replicazione Formule Excel)
# ==============================================================================

# --- A. REGIME ORDINARIO ---
reddito_lav_autonomo = ricavi_compensi - costi_spese # (A-B)
# Reddito imponibile = Reddito - Contributi INPS (Oneri deducibili)
reddito_imponibile_ord = reddito_lav_autonomo - inps_ordinario

# Calcolo IRPEF Lorda (Scaglione 2024 semplificato: 23% fino a 28k)
irpef_lorda = reddito_imponibile_ord * 0.23

# Totale Detrazioni
totale_detrazioni = detraz_oneri + detraz_lav_autonomo

# IRPEF Netta (non può essere negativa)
irpef_netta = max(0, irpef_lorda - totale_detrazioni)

# Addizionali
addizionale_reg = reddito_imponibile_ord * (aliq_add_regionale / 100)
addizionale_com = reddito_imponibile_ord * (aliq_add_comunale / 100)
totale_addizionali = addizionale_reg + addizionale_com

# Totale Imposte Dirette Ordinario
totale_imposte_ord = irpef_netta + totale_addizionali

# COSTO TOTALE ORDINARIO (Tasse + INPS)
costo_totale_ordinario = totale_imposte_ord + inps_ordinario


# --- B. REGIME FORFETTARIO ---
# Ricavi Forfettario (C) = Ricavi + IVA che non versi più
ricavi_lordi_forf = ricavi_compensi + iva_a_debito 

# Imponibile Lordo (D)
imponibile_lordo_forf = ricavi_lordi_forf * (coeff_redditivita / 100)

# Imponibile Netto (D - E) -> Reddito su cui paghi le tasse
# Nota: L'INPS è deducibile. Nel file excel lo sottrae.
imponibile_netto_forf = imponibile_lordo_forf - inps_forfettario

# Imposta Sostitutiva
imposta_sostitutiva = imponibile_netto_forf * (aliquota_sostitutiva / 100)

# Effetto IVA (Guadagno IVA vendite - Perdita IVA acquisti)
effetto_iva = iva_a_debito - iva_a_credito

# COSTO TOTALE FORFETTARIO
# Formula: Tasse + INPS - (Soldi dell'IVA che ti sono rimasti in tasca)
costo_totale_forfettario = (imposta_sostitutiva + inps_forfettario) - effetto_iva


# ==============================================================================
# 3. INTERFACCIA GRAFICA RISULTATI
# ==============================================================================

# Colonne per confronto visivo
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏛️ Regime Ordinario")
    st.write("---")
    st.write(f"Reddito Lavoro Autonomo (A-B): **{reddito_lav_autonomo:,.0f} €**")
    st.write(f"Oneri Deducibili (INPS): **-{inps_ordinario:,.0f} €**")
    st.write(f"Reddito Imponibile: **{reddito_imponibile_ord:,.0f} €**")
    st.write(f"IRPEF Lorda: **{irpef_lorda:,.0f} €**")
    st.write(f"Totale Detrazioni: **-{totale_detrazioni:,.0f} €**")
    st.write(f"IRPEF Netta: **{irpef_netta:,.0f} €**")
    st.write(f"Addizionali (Reg+Com): **{totale_addizionali:,.0f} €**")
    st.write("---")
    st.info(f"Totale Imposte Dirette: {totale_imposte_ord:,.0f} €")
    st.error(f"TOTALE USCITE (Tasse + INPS): {costo_totale_ordinario:,.0f} €")

with col2:
    st.markdown("### 🚀 Regime Forfettario")
    st.write("---")
    st.write(f"Ricavi Lordi (C) [A + IVA Debito]: **{ricavi_lordi_forf:,.0f} €**")
    st.write(f"Imponibile Lordo (D) [coeff {coeff_redditivita}%]: **{imponibile_lordo_forf:,.0f} €**")
    st.write(f"Contributi INPS (E): **-{inps_forfettario:,.0f} €**")
    st.write(f"Imponibile Netto (D-E): **{imponibile_netto_forf:,.0f} €**")
    st.write(f"Imposta Sostitutiva ({aliquota_sostitutiva}%): **{imposta_sostitutiva:,.0f} €**")
    st.success(f"Effetto IVA (Incassata - Persa): **-{effetto_iva:,.0f} €** (Guadagno)")
    st.write("---")
    st.info(f"Totale Imposta Sostitutiva: {imposta_sostitutiva:,.0f} €")
    
    # Calcolo visivo per capire il "Costo Reale"
    st.error(f"TOTALE USCITE REALI (Tasse+INPS-IVA): {costo_totale_forfettario:,.0f} €")

# ==============================================================================
# 4. VERDETTO FINALE
# ==============================================================================
st.divider()

differenza = costo_totale_ordinario - costo_totale_forfettario

col_res1, col_res2 = st.columns([3, 1])

with col_res1:
    if differenza > 0:
        st.balloons()
        st.markdown(f"## ✅ RISPARMIO CON FORFETTARIO: +{differenza:,.2f} €")
        st.caption("Il forfettario ti lascia più soldi in tasca rispetto all'ordinario.")
    else:
        st.markdown(f"## ❌ PERDITA CON FORFETTARIO: {differenza:,.2f} €")
        st.markdown("### 💡 Il Regime Ordinario CONVIENE ancora.")
        st.warning(f"Motivo principale: Le tue detrazioni ({totale_detrazioni:,.0f}€) azzerano le tasse nell'ordinario, mentre nel forfettario paghi comunque il 15%.")
        
        if not riduzione_inps_35 and not usa_inps_manuale:
             st.markdown("👉 **Suggerimento:** Prova a spuntare 'Richiedi riduzione INPS 35%' nella barra laterale. Potrebbe ribaltare il risultato!")

with col_res2:
    st.metric(label="Differenza Netta", value=f"{differenza:,.0f} €", delta_color="normal")

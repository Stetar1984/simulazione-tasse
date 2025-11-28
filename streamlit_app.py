import streamlit as st

# Titolo della pagina
st.title("Calcolatore Convenienza Fiscale 🇮🇹")
st.subheader("Confronto Ordinario vs Forfettario (Parrucchieri)")

# --- COLONNA LATERALE PER GLI INPUT ---
with st.sidebar:
    st.header("1. Inserisci i tuoi dati")
    ricavi_netti = st.number_input("Ricavi/Compensi (senza IVA)", value=33616)
    costi_reali = st.number_input("Costi/Spese Reali", value=19076)
    iva_incassata = st.number_input("IVA Incassata dai clienti", value=7395)
    iva_acquisti = st.number_input("IVA pagata sugli acquisti", value=2600)
    
    st.header("2. Dati Personali")
    altre_detrazioni = st.number_input("Totale Detrazioni (Spese mediche, figli, ecc.)", value=2635)
    
    st.header("3. Opzioni Forfettario")
    richiedi_riduzione_inps = st.checkbox("Richiedi riduzione INPS 35%?", value=False)
    coeff_redditivita = 0.67
    aliquota_sostitutiva = 0.15 # 15%
    aliquota_inps = 0.24 # 24% circa artigiani

# --- CALCOLI (DIETRO LE QUINTE) ---

# 1. Calcolo Ordinario
reddito_ord = ricavi_netti - costi_reali
inps_ord = reddito_ord * aliquota_inps
imp_irpef = reddito_ord - inps_ord
irpef_lorda = imp_irpef * 0.23 # Scaglione 23%
detr_lavoro = 890 # Stima
irpef_netta = max(0, irpef_lorda - (altre_detrazioni + detr_lavoro))
addizionali = imp_irpef * 0.0173
totale_tasse_ord = irpef_netta + addizionali + inps_ord

# 2. Calcolo Forfettario
ricavi_forf = ricavi_netti + iva_incassata
imp_forf = ricavi_forf * coeff_redditivita
inps_forf = imp_forf * aliquota_inps
if richiedi_riduzione_inps:
    inps_forf = inps_forf * 0.65

imp_netto_forf = imp_forf - inps_forf
tassa_flat = imp_netto_forf * aliquota_sostitutiva
beneficio_iva = iva_incassata - iva_acquisti
# Costo reale = Tasse + INPS - (Soldi IVA che ti rimangono in tasca)
costo_reale_forf = (tassa_flat + inps_forf) - beneficio_iva

# --- RISULTATI A VIDEO ---
col1, col2 = st.columns(2)

with col1:
    st.info("🏛️ REGIME ORDINARIO")
    st.write(f"Imponibile IRPEF: **{imp_irpef:,.2f} €**")
    st.write(f"INPS: {inps_ord:,.2f} €")
    st.write(f"IRPEF + Addiz.: {irpef_netta+addizionali:,.2f} €")
    st.error(f"COSTO TOTALE: {totale_tasse_ord:,.2f} €")

with col2:
    st.success("🚀 REGIME FORFETTARIO")
    st.write(f"Nuovi Ricavi (con IVA): **{ricavi_forf:,.2f} €**")
    st.write(f"Imponibile (67%): {imp_forf:,.2f} €")
    st.write(f"INPS {'(Ridotta)' if richiedi_riduzione_inps else ''}: {inps_forf:,.2f} €")
    st.write(f"Imposta 15%: {tassa_flat:,.2f} €")
    st.write(f"Vantaggio IVA: -{beneficio_iva:,.2f} €")
    st.error(f"COSTO REALE: {costo_reale_forf:,.2f} €")

st.markdown("---")
differenza = totale_tasse_ord - costo_reale_forf

if differenza > 0:
    st.balloons()
    st.title(f"✅ Conviene il Forfettario!")
    st.header(f"Risparmi: {differenza:,.2f} € all'anno")
else:
    st.title(f"❌ Conviene l'Ordinario")
    st.header(f"Col forfettario perderesti: {abs(differenza):,.2f} €")
    st.write("Motivo: Le tue detrazioni personali nell'ordinario sono molto alte e azzerano le tasse.")

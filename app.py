import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Bilancio Parrocchiale", 
    page_icon="⛪", 
    layout="wide"
)

# --- 2. PERSONALIZZAZIONE ESTETICA (CSS) ---
# Qui puoi cambiare i colori: 
# #2c3e50 è un blu scuro professionale, #ffffff è il bianco
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    h1 { color: #2c3e50; }
    </style>
    """, unsafe_allow_input=True)

# --- 3. CARICAMENTO DATI ---
# INSERISCI QUI IL TUO LINK COPIATO DA GOOGLE SHEETS
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdOvvH12V14IK6aAnK-22kmQNhoLiya9rHcV9ONHNMwU_QT4vx4jDDXz6SBj1az_Ln9fLlOzayxI3L/pub?output=csv"

@st.cache_data(ttl=60)  # Aggiorna i dati ogni 60 secondi
def load_data(url):
    df = pd.read_csv(url)
    # Convertiamo la colonna Data in formato leggibile dal computer
    df['Data'] = pd.to_datetime(df['Data'])
    return df

# --- 4. INTERFACCIA UTENTE ---
st.title("⛪ Bilancio Parrocchiale Trasparente")
st.write("Benvenuti nella pagina dedicata alla trasparenza dei fondi della nostra comunità.")

try:
    df = load_data(URL_FOGLIO)

    # Calcoli per le "mattonelle" in alto
    entrate = df[df['Importo'] > 0]['Importo'].sum()
    uscite = abs(df[df['Importo'] < 0]['Importo'].sum())
    saldo = entrate - uscite

    # Visualizzazione Metriche
    col1, col2, col3 = st.columns(3)
    col1.metric("Totale Entrate", f"€ {entrate:,.2f}")
    col2.metric("Totale Uscite", f"€ {uscite:,.2f}", delta_color="inverse")
    col3.metric("Saldo Attuale", f"€ {saldo:,.2f}")

    st.divider()

    # --- 5. GRAFICI ---
    col_sx, col_dx = st.columns(2)

    with col_sx:
        st.subheader("Andamento nel tempo")
        # Grafico a linee per vedere come variano i fondi
        fig_linea = px.line(df, x='Data', y='Importo', markers=True, 
                             color_discrete_sequence=['#2c3e50'])
        st.plotly_chart(fig_linea, use_container_width=True)

    with col_dx:
        st.subheader("Distribuzione per Categoria")
        # Grafico a torta per vedere dove finiscono i soldi
        # Filtriamo solo le uscite per il grafico a torta
        df_uscite = df[df['Importo'] < 0].copy()
        df_uscite['Importo'] = abs(df_uscite['Importo'])
        fig_torta = px.pie(df_uscite, values='Importo', names='Categoria', 
                           hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_torta, use_container_width=True)

    st.divider()

    # --- 6. TABELLA DETTAGLIATA ---
    st.subheader("Cronologia Operazioni")
    # Ordiniamo per data più recente
    df_mostra = df.sort_values(by='Data', ascending=False)
    st.dataframe(df_mostra, use_container_width=True)

except Exception as e:
    st.error("Ops! Qualcosa non va con il link di Google Sheets.")
    st.info("Assicurati di aver impostato 'Valori separati da virgola (.csv)' nella pubblicazione web.")
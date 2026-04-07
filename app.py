import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Rendiconto Parrocchiale",
    page_icon="⛪",
    layout="wide"
)

# --- 2. CODICE "INVISIBILITÀ" (ORA CORRETTO: unsafe_allow_html=True) ---
st.markdown("""
    <style>
    /* Nasconde il tasto GitHub e il menu in alto a destra */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Rimuove i pulsanti fluttuanti di Streamlit */
    .stAppDeployButton {display:none;}
    [data-testid="stDecoration"] {display:none !important;}
    [data-testid="stToolbar"] {display:none !important;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. TITOLO E CONTENUTO ---
st.title("⛪ Bilancio Trasparente della Parrocchia")
st.write("Riepilogo delle entrate e donazioni della nostra comunità.")

# INSERISCI QUI IL TUO LINK CSV
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRxmWYgGezaj5koTH_jaPV6cB6mYbb0s3mor-9yR8X-Op1Jrhhc4a1A3DaNdXt9lR_pkKssPX2tbOP6/pub?gid=0&single=true&output=csv"

def load_data_robust(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return pd.DataFrame()
        df = pd.read_csv(io.StringIO(response.text))
        if not df.empty:
            # Pulizia forzata dei numeri (Gestisce le virgole europee)
            df['Importo'] = df['Importo'].astype(str).str.replace(',', '.')
            df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            df = df.dropna(subset=['Importo', 'Data'])
        return df
    except:
        return pd.DataFrame()

df = load_data_robust(URL_FOGLIO)

if not df.empty:
    # Calcolo Totale
    totale_entrate = df['Importo'].sum()
    st.metric("Fondi Totali Raccolti", f"€ {totale_entrate:,.2f}")
    st.divider()

    # Raggruppamento per Categoria
    df_categorie = df.groupby('Categoria')['Importo'].sum().reset_index()
    df_categorie = df_categorie.sort_values(by='Importo', ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Distribuzione %")
        fig_pie = px.pie(df_categorie, values='Importo', names='Categoria', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("📈 Totali per Categoria")
        fig_bar = px.bar(df_categorie, x='Categoria', y='Importo', color='Categoria')
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.subheader("📑 Dettaglio Cronologico")
    st.dataframe(
        df.sort_values(by='Data', ascending=False)[['Data', 'Descrizione', 'Categoria', 'Importo']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Caricamento dati in corso... (Se ci mette molto, fai una piccola modifica sul foglio Google per 'svegliarlo')")

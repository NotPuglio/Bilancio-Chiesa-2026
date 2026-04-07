import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Bilancio Chiesa Cristiana Avventista di Parma",
    page_icon="⛪",
    layout="wide"
)

# --- 2. CODICE "INVISIBILITÀ" E ALLINEAMENTO LOGO (CSS) ---
# Ho aggiunto una regola specifica (.stImage) per forzare l'allineamento a destra
st.markdown("""
    <style>
    /* Nasconde Header, Menu e Footer */
    [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stDecoration"] {display:none !important;}
    [data-testid="stToolbar"] {display:none !important;}
    
    /* TRUCCO PER IL LOGO: Forza l'allineamento a destra nella colonna */
    [data-testid="column"]:last-of-type div.stImage {
        text-align: right;
        display: flex;
        justify-content: flex-end;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. TITOLO E LOGO PICCOLO (Affiancati) ---
# Usiamo una proporzione drastica (10 a 1) per tenere la colonna del logo stretta
col_testo, col_logo = st.columns([10, 1])

with col_testo:
    st.title("⛪ Entrate raccolte durante le offerte")
    st.write("Riepilogo delle entrate e donazioni della nostra comunità.")

with col_logo:
# --- MODIFICA QUI ---
    # Abbiamo rimosso 'use_container_width=True'
    # Abbiamo aggiunto 'width=80' (pixel). Puoi cambiare questo numero per regolarlo.
    st.image("adventist-symbol--black.svg", width=80)

# INSERISCI QUI IL TUO LINK CSV
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRxmWYgGezaj5koTH_jaPV6cB6mYbb0s3mor-9yR8X-Op1Jrhhc4a1A3DaNdXt9lR_pkKssPX2tbOP6/pub?gid=0&single=true&output=csv"

def load_data_robust(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return pd.DataFrame()
        df = pd.read_csv(io.StringIO(response.text))
        if not df.empty:
            # Pulizia numeri (gestisce virgole e punti)
            df['Importo'] = df['Importo'].astype(str).str.replace(',', '.')
            df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)
            # Conversione Date (fondamentale per il raggruppamento)
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce').dt.date
            df = df.dropna(subset=['Importo', 'Data'])
        return df
    except:
        return pd.DataFrame()

df = load_data_robust(URL_FOGLIO)

if not df.empty:
    # --- CALCOLO TOTALE GENERALE ---
    totale_entrate = df['Importo'].sum()
    st.metric("Fondi Totali Raccolti nel 2026", f"€ {totale_entrate:,.2f}")
    st.divider()

    # --- GRAFICI (RAGGRUPPATI PER CATEGORIA) ---
    df_categorie = df.groupby('Categoria')['Importo'].sum().reset_index()
    df_categorie = df_categorie.sort_values(by='Importo', ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Distribuzione %")
        fig_pie = px.pie(df_categorie, values='Importo', names='Categoria', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("📈 Andamento Giornaliero")
        # NUOVO ISTOGRAMMA: Raggruppiamo per Data E Categoria
        df_andamento = df.groupby(['Data', 'Categoria'])['Importo'].sum().reset_index()
        
        fig_bar = px.bar(
            df_andamento, 
            x='Data', 
            y='Importo', 
            color='Categoria',
            barmode='group', # Mette le colonne affiancate per lo stesso giorno
            labels={'Importo': 'Incasso (€)'}
        )
        
        # Rendiamo l'asse X (Date) più leggibile, togliamo i numeri automatici sopra le barre 
        # perché sarebbero troppi, e mettiamo la legenda in basso
        fig_bar.update_layout(
            xaxis_title="Data",
            yaxis_title="Euro",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        # Forza Plotly a mostrare le barre per ogni data senza raggrupparle per mese
        fig_bar.update_xaxes(type='category')
        
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    
    # Cronologia giornaliera (invariata)
    st.subheader("📑 Totale giornaliero entrate")
    df_giornaliero = df.groupby('Data')['Importo'].sum().reset_index()
    df_giornaliero = df_giornaliero.sort_values(by='Data', ascending=False)
    
    st.dataframe(
        df_giornaliero,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Data": st.column_config.DateColumn("Giorno"),
            "Importo": st.column_config.NumberColumn("Totale Incassato", format="€ %.2f")
        }
    )
else:
    st.info("Caricamento dati in corso...")
else:
    st.info("Caricamento dati in corso...")

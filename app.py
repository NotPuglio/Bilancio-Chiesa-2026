import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# --- 1. CONFIGURAZIONE ESTETICA ---
st.set_page_config(
    page_title="Rendiconto Parrocchiale",
    page_icon="⛪",
    layout="wide" 
)

# Nascondiamo i menu di sistema per rendere la pagina più pulita (Richiesta precedente)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { color: #1a5276; }
    </style>
    """, unsafe_allow_input=True)

# --- 2. CARICAMENTO DATI ---
# Sostituisci con il tuo link che finisce in output=csv
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdOvvH12V14IK6aAnK-22kmQNhoLiya9rHcV9ONHNMwU_QT4vx4jDDXz6SBj1az_Ln9fLlOzayxI3L/pub?output=csv"

def load_data(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            # Pulizia forzata dei numeri (gestisce virgole e punti)
            df['Importo'] = df['Importo'].astype(str).str.replace(',', '.')
            df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            return df.dropna(subset=['Importo', 'Data'])
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 3. LOGICA PRINCIPALE ---
st.title("⛪ Bilancio Trasparente della Parrocchia")
st.write("Riepilogo settimanale delle entrate e donazioni.")

df = load_data(URL_FOGLIO)

if not df.empty:
    # --- CALCOLI TOTALI ---
    # Python sommerà tutte le righe, anche se hanno la stessa data
    totale_entrate = df[df['Importo'] > 0]['Importo'].sum()
    
    # Metrica principale in alto
    st.metric("Fondi Totali Raccolti", f"€ {totale_entrate:,.2f}")
    st.divider()

    # --- ANALISI PER CATEGORIA (Somma automatica) ---
    # Raggruppiamo i dati: Python somma i valori per ogni categoria trovata
    df_categorie = df.groupby('Categoria')['Importo'].sum().reset_index()
    # Ordiniamo dalla categoria più generosa alla minore
    df_categorie = df_categorie.sort_values(by='Importo', ascending=False)

    col_sx, col_dx = st.columns(2)

    with col_sx:
        st.subheader("📊 Suddivisione Percentuale")
        # Grafico a Torta (Pie Chart)
        fig_pie = px.pie(
            df_categorie, 
            values='Importo', 
            names='Categoria',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_dx:
        st.subheader("📈 Istogramma Entrate")
        # Istogramma (Bar Chart)
        fig_bar = px.bar(
            df_categorie, 
            x='Categoria', 
            y='Importo',
            color='Categoria',
            text_auto='.2f', # Mostra il valore sopra la barra
            labels={'Importo': 'Totale (€)'}
        )
        # Rendiamo l'istogramma più pulito
        fig_bar.update_layout(showlegend=False) 
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- TABELLA CRONOLOGICA ---
    st.subheader("📑 Dettaglio delle ultime offerte")
    # Ordiniamo per data (più recente in alto)
    df_tabella = df.sort_values(by='Data', ascending=False)
    
    # Formattiamo la tabella per smartphone
    st.dataframe(
        df_tabella[['Data', 'Descrizione', 'Categoria', 'Importo']],
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("In attesa del caricamento dei dati da Google Sheets...")

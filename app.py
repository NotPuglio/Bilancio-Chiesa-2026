import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# --- 1. CONFIGURAZIONE ESTETICA ---
st.set_page_config(
    page_title="Bilancio Parrocchiale Online",
    page_icon="⛪",
    layout="centered" # "centered" è più elegante per questo tipo di report
)

# CSS personalizzato per nascondere il menu Streamlit e pulire i font
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #1a5276; }
    h1, h2, h3 { color: #1a5276; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    </style>
    """, unsafe_allow_input=True)

# --- 2. CARICAMENTO DATI (Senza Cache per massima freschezza) ---
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdOvvH12V14IK6aAnK-22kmQNhoLiya9rHcV9ONHNMwU_QT4vx4jDDXz6SBj1az_Ln9fLlOzayxI3L/pub?output=csv"

def load_clean_data(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            if not df.empty:
                # Pulizia formati
                df['Importo'] = df['Importo'].astype(str).str.replace(',', '.')
                df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)
                df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
                df = df.dropna(subset=['Importo', 'Data'])
                return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 3. LOGICA DELL'APP ---
st.title("⛪ Rendiconto Finanziario")
st.write("Iniziativa di trasparenza per la nostra comunità parrocchiale.")
st.divider()

df = load_clean_data(URL_FOGLIO)

if not df.empty:
    # --- CALCOLI ---
    entrate = df[df['Importo'] > 0]['Importo'].sum()
    uscite = abs(df[df['Importo'] < 0]['Importo'].sum())
    saldo = entrate - uscite

    # --- VISUALIZZAZIONE METRICHE ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Totale Entrate", f"€ {entrate:,.2f}")
    c2.metric("Totale Uscite", f"€ {uscite:,.2f}")
    c3.metric("Fondo Cassa attuale", f"€ {saldo:,.2f}")

    st.divider()

    # --- GRAFICI ---
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Entrate vs Uscite")
        # Un grafico a torta per mostrare la natura dei movimenti
        df_pie = df.copy()
        df_pie['Tipo'] = df_pie['Importo'].apply(lambda x: 'Entrata' if x > 0 else 'Uscita')
        df_pie['Valore'] = df_pie['Importo'].abs()
        fig_pie = px.pie(df_pie, values='Valore', names='Tipo', 
                         color_discrete_map={'Entrata':'#2ecc71', 'Uscita':'#e74c3c'},
                         hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.subheader("Spese per Categoria")
        # Solo uscite per capire dove vanno i soldi
        df_uscite = df[df['Importo'] < 0].copy()
        df_uscite['Importo'] = df_uscite['Importo'].abs()
        fig_cat = px.bar(df_uscite, x='Categoria', y='Importo', 
                         color_discrete_sequence=['#3498db'])
        st.plotly_chart(fig_cat, use_container_width=True)

    # --- TABELLA FINALE ---
    st.subheader("Cronologia delle ultime operazioni")
    st.dataframe(
        df.sort_values(by='Data', ascending=False)[['Data', 'Descrizione', 'Categoria', 'Importo']],
        use_container_width=True,
        hide_index=True
    )
    
    st.info("I dati vengono aggiornati periodicamente dal consiglio parrocchiale.")

else:
    st.error("⚠️ Servizio momentaneamente non disponibile. Riprova più tardi.")

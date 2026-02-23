import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Bilancio Parrocchiale", page_icon="⛪", layout="wide")

st.title("⛪ Bilancio Parrocchiale")
st.write("Versione con sistema di controllo avanzato")

# --- 2. IL TUO LINK (Assicurati che finisca con output=csv) ---
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdOvvH12V14IK6aAnK-22kmQNhoLiya9rHcV9ONHNMwU_QT4vx4jDDXz6SBj1az_Ln9fLlOzayxI3L/pub?output=csv"

# --- 3. PROVA DEL NOVE: FUNZIONE DI CARICAMENTO DIRETTO ---
def load_data_robust(url):
    try:
        # Forziamo il download saltando ogni memoria temporanea (cache)
        response = requests.get(url, timeout=10)
        
        # Se Google risponde con un errore (es. 404 o 400) lo vedremo qui
        if response.status_code != 200:
            st.error(f"⚠️ Errore di connessione a Google Sheets: Codice {response.status_code}")
            return pd.DataFrame() # Restituisce una tabella vuota in caso di errore
            
        # Leggiamo il testo ricevuto
        testo_dati = response.text
        
        # Creiamo la tabella (DataFrame)
        df = pd.read_csv(io.StringIO(testo_dati))
        
        # Pulizia forzata dei dati
        if not df.empty:
            # Rimuove righe totalmente vuote
            df = df.dropna(how='all')
            # Converte Importo in numero (gestendo virgole e punti)
            df['Importo'] = df['Importo'].astype(str).str.replace(',', '.')
            df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)
            # Converte Data
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"❌ Errore critico nel caricamento: {e}")
        return pd.DataFrame()

# --- 4. ESECUZIONE E DEBUG ---
df = load_data_robust(URL_FOGLIO)

# Area di monitoraggio (la rimuoveremo quando tutto sarà ok)
with st.expander("🔍 Pannello di Controllo (Clicca per vedere i dati grezzi)"):
    st.write(f"Stato: {'✅ Dati ricevuti' if not df.empty else '❌ Tabella vuota'}")
    st.write("Righe totali trovate:", len(df))
    st.write("Colonne trovate:", df.columns.tolist())
    st.dataframe(df)

if not df.empty:
    # --- 5. CALCOLI E VISUALIZZAZIONE ---
    entrate = df[df['Importo'] > 0]['Importo'].sum()
    uscite = abs(df[df['Importo'] < 0]['Importo'].sum())
    saldo = entrate - uscite

    # Metriche
    c1, c2, c3 = st.columns(3)
    c1.metric("Entrate", f"€ {entrate:,.2f}")
    c2.metric("Uscite", f"€ {uscite:,.2f}")
    c3.metric("Saldo Attuale", f"€ {saldo:,.2f}")

    st.divider()

    # Grafico
    st.subheader("Andamento Fondi")
    fig = px.bar(df, x='Data', y='Importo', color='Categoria', barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    # Tabella
    st.subheader("Dettaglio Movimenti")
    st.dataframe(df.sort_values(by='Data', ascending=False), use_container_width=True)
else:
    st.warning("⚠️ Il sistema non ha trovato dati. Verifica il link su GitHub e la pubblicazione su Google Sheets.")

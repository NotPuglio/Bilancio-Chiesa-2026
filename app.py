import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configurazione della pagina
st.set_page_config(page_title="Bilancio Parrocchiale", page_icon="⛪", layout="centered")

# 2. Titolo (Senza CSS complicato che dava errore)
st.title("⛪ Bilancio Parrocchiale")
st.info("Trasparenza finanziaria per la nostra comunità.")

# 3. LINK DATI
# ATTENZIONE: Incolla qui il tuo link che finisce con output=csv
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdOvvH12V14IK6aAnK-22kmQNhoLiya9rHcV9ONHNMwU_QT4vx4jDDXz6SBj1az_Ln9fLlOzayxI3L/pub?output=csv"

# 4. Funzione di caricamento "Blindata"
@st.cache_data(ttl=60)
def load_data(url):
    # Legge il CSV
    try:
        df = pd.read_csv(url)
    except Exception as e:
        st.error(f"Errore di connessione: {e}")
        return pd.DataFrame()

    # --- PULIZIA IMPORTI (Risolve l'errore str vs int) ---
    # Convertiamo tutto in testo per sicurezza
    df['Importo'] = df['Importo'].astype(str)
    # Sostituiamo la virgola con il punto (formato internazionale)
    df['Importo'] = df['Importo'].str.replace(',', '.', regex=False)
    # Rimuoviamo eventuali simboli € o spazi
    df['Importo'] = df['Importo'].str.replace('€', '', regex=False).str.strip()
    # Trasformiamo finalmente in numero. Se c'è un errore, mette 0 (coerce)
    df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)

    # --- PULIZIA DATE ---
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    
    # Rimuoviamo righe vuote o sbagliate
    df = df.dropna(subset=['Data', 'Importo'])
    
    return df

# 5. Esecuzione
try:
    df = load_data(URL_FOGLIO)

    if not df.empty:
        # Calcoli
        entrate = df[df['Importo'] > 0]['Importo'].sum()
        uscite = abs(df[df['Importo'] < 0]['Importo'].sum())
        saldo = entrate - uscite

        # Metriche
        col1, col2, col3 = st.columns(3)
        col1.metric("Entrate", f"€ {entrate:,.2f}")
        col2.metric("Uscite", f"€ {uscite:,.2f}")
        col3.metric("Saldo", f"€ {saldo:,.2f}")

        st.divider()

        # Grafico a Torta (Entrate vs Uscite)
        st.subheader("Riepilogo")
        # Creiamo un piccolo dataframe per il grafico
        dati_grafico = pd.DataFrame({
            'Tipo': ['Entrate', 'Uscite'],
            'Valore': [entrate, uscite]
        })
        fig = px.pie(dati_grafico, values='Valore', names='Tipo', 
                     color='Tipo',
                     color_discrete_map={'Entrata':'#2ecc71', 'Uscita':'#e74c3c'})
        st.plotly_chart(fig, use_container_width=True)

        # Tabella
        st.subheader("Ultimi Movimenti")
        st.dataframe(df.sort_values(by='Data', ascending=False), use_container_width=True)
    
    else:
        st.warning("Nessun dato trovato. Controlla il link di Google Sheets.")

except Exception as e:
    st.error(f"Qualcosa è andato storto: {e}")

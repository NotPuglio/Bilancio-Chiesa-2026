import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bilancio Parrocchiale", page_icon="⛪")

st.title("⛪ Bilancio Parrocchiale")
st.write("Pagina per la trasparenza finanziaria della comunità.")

# INSERISCI QUI IL TUO LINK CSV
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdOvvH12V14IK6aAnK-22kmQNhoLiya9rHcV9ONHNMwU_QT4vx4jDDXz6SBj1az_Ln9fLlOzayxI3L/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    # Carichiamo i dati
    df = pd.read_csv(url)
    
    # PULIZIA DATI (Risolve l'errore dello screenshot)
    # Trasforma la colonna Importo in testo, toglie punti/virgole e la converte in numero decimale
    df['Importo'] = df['Importo'].astype(str).str.replace(',', '.')
    df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce')
    
    # Converte la data
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    
    # Elimina eventuali righe vuote
    df = df.dropna(subset=['Importo', 'Data'])
    return df

try:
    df = load_data(URL_FOGLIO)

    # Calcoli
    entrate = df[df['Importo'] > 0]['Importo'].sum()
    uscite = abs(df[df['Importo'] < 0]['Importo'].sum())
    saldo = entrate - uscite

    # Metriche
    c1, c2, c3 = st.columns(3)
    c1.metric("Entrate", f"€ {entrate:,.2f}")
    c2.metric("Uscite", f"€ {uscite:,.2f}")
    c3.metric("Saldo", f"€ {saldo:,.2f}")

    st.divider()

    # Grafico a barre (più chiaro per i bilanci)
    st.subheader("Andamento Fondi")
    fig = px.bar(df, x='Data', y='Importo', color='Categoria', barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    # Tabella
    st.subheader("Dettaglio Movimenti")
    st.dataframe(df.sort_values(by='Data', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Errore tecnico: {e}")
    st.info("Controlla che i numeri nel foglio non abbiano il simbolo € scritto a mano.")

import streamlit as st
import pandas as pd
import plotly.express as px

# Configurazione base
st.set_page_config(page_title="Bilancio Parrocchiale", page_icon="⛪")

# Rimuoviamo il blocco CSS che causava l'errore e usiamo i comandi nativi
st.title("⛪ Bilancio Parrocchiale")
st.write("Pagina per la trasparenza finanziaria della comunità.")

# INSERISCI QUI IL TUO LINK CSV
URL_FOGLIO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQdOvvH12V14IK6aAnK-22kmQNhoLiya9rHcV9ONHNMwU_QT4vx4jDDXz6SBj1az_Ln9fLlOzayxI3L/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    # Leggiamo il CSV
    data = pd.read_csv(url)
    # Pulizia minima delle date
    data['Data'] = pd.to_datetime(data['Data'])
    return data

try:
    df = load_data(URL_FOGLIO)

    # Calcoli
    entrate = df[df['Importo'] > 0]['Importo'].sum()
    uscite = abs(df[df['Importo'] < 0]['Importo'].sum())
    saldo = entrate - uscite

    # Metriche (Semplici e pulite)
    c1, c2, c3 = st.columns(3)
    c1.metric("Entrate", f"€ {entrate:,.2f}")
    c2.metric("Uscite", f"€ {uscite:,.2f}")
    c3.metric("Saldo", f"€ {saldo:,.2f}")

    # Grafico
    st.subheader("Andamento Fondi")
    fig = px.area(df, x='Data', y='Importo', color_discrete_sequence=['#007bff'])
    st.plotly_chart(fig, use_container_width=True)

    # Tabella
    st.subheader("Dettaglio Movimenti")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Errore: {e}")
    st.info("Verifica che il link sia corretto e che le colonne nel foglio siano: Data, Descrizione, Categoria, Importo")

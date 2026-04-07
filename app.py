import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# --- 1. CONFIGURAZIONE PAGINA (Metodo sicuro) ---
st.set_page_config(
    page_title="Rendiconto parma",
    page_icon="⛪",
    layout="wide"
)

# Titolo semplice per evitare errori di markdown/CSS
st.title("⛪ Bilancio Trasparente della Parrocchia")
st.write("Riepilogo delle entrate e donazioni della nostra comunità.")

# --- 2. LINK DATI (Ricordati di inserire il tuo link CSV) ---
URL_FOGLIO = "IL_TUO_LINK_QUI"

# --- 3. CARICAMENTO E PULIZIA DATI ---
def load_data_robust(url):
    try:
        # Carichiamo i dati freschi saltando la cache in caso di errori
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            st.error("Errore di connessione a Google Sheets.")
            return pd.DataFrame()
        
        df = pd.read_csv(io.StringIO(response.text))
        
        if not df.empty:
            # Pulizia forzata degli Importi (risolve l'errore str vs int)
            df['Importo'] = df['Importo'].astype(str).str.replace(',', '.')
            df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)
            
            # Conversione Date
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            
            # Rimuoviamo righe totalmente vuote
            df = df.dropna(subset=['Importo', 'Data'])
            
        return df
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
        return pd.DataFrame()

# Esecuzione caricamento
df = load_data_robust(URL_FOGLIO)

# --- 4. VISUALIZZAZIONE ---
if not df.empty:
    # Calcolo Totale (Somma tutte le righe, anche con stessa data)
    totale_entrate = df['Importo'].sum()
    
    st.metric("Fondi Totali Raccolti", f"€ {totale_entrate:,.2f}")
    st.divider()

    # Raggruppamento per Categoria (Somma automatica delle voci simili)
    df_categorie = df.groupby('Categoria')['Importo'].sum().reset_index()
    df_categorie = df_categorie.sort_values(by='Importo', ascending=False)

    # Layout a due colonne per i grafici
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Distribuzione %")
        fig_pie = px.pie(
            df_categorie, 
            values='Importo', 
            names='Categoria',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("📈 Totali per Categoria")
        fig_bar = px.bar(
            df_categorie, 
            x='Categoria', 
            y='Importo',
            text_auto='.2f',
            color='Categoria',
            labels={'Importo': 'Totale (€)'}
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # Tabella Dettagliata (Dati grezzi riga per riga)
    st.subheader("📑 Dettaglio Cronologico")
    st.dataframe(
        df.sort_values(by='Data', ascending=False)[['Data', 'Descrizione', 'Categoria', 'Importo']],
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("In attesa dei dati... Verifica che il link sia corretto e il file Google Sheets sia pubblico.")

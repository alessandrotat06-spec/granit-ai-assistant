import streamlit as st
import pandas as pd
from google import genai

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Granit Quality Parts - Assistente IA", page_icon="🚜", layout="centered")

st.title("🚜 Granit Quality Parts - Assistente IA")
st.write("Cerca i ricambi nel catalogo ufficiale in modo istantaneo.")

# Configurazione della chiave API di Google
client = genai.Client(api_key="AQ.Ab8RN6JavzpWb7CgSW_1z7AYBuLUMP5UQ8KTcye9Xh28Tg_hFg")

# Caricamento pulito del catalogo CSV con Pandas
@st.cache_data
def carica_catalogo():
    try:
        df = pd.read_csv('catalogo_granit.csv')
        return df
    except Exception as e:
        return None

df_catalogo = carica_catalogo()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query := st.chat_input("Cerca un ricambio (es. anello in gomma, tampone, staffa)..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Sto cercando nel catalogo..."):
            
            # RICERCA DIRETTA NEL CSV (estrae i dati reali al 100% senza che l'IA debba inventare o fallire la lettura)
            risultati_trovati = []
            if df_catalogo is not None:
                query_lower = user_query.lower()
                # Cerca se le parole chiave dell'utente compaiono nella descrizione o nel codice
                parole = [p for p in query_lower.split() if len(p) > 2]
                
                for _, row in df_catalogo.iterrows():
                    riga_testo = f"{row.get('Codice', '')} {row.get('Rif_Orig', '')} {row.get('Descrizione', '')} {row.get('Modelli_Compatibilita', '')}".lower()
                    if any(parola in riga_testo for parola in parole):
                        risultati_trovati.append(row)

            if risultati_trovati:
                testo_risposta = "Ecco i ricambi trovati nel catalogo ufficiale:\n\n"
                # Mostriamo fino a un massimo di 5 risultati pertinenti
                for r in risultati_trovati[:5]:
                    testo_risposta += f"- **Codice Articolo:** {r.get('Codice', 'N/D')}\n"
                    if pd.notna(r.get('Rif_Orig')) and str(r.get('Rif_Orig')) != '':
                        testo_risposta += f"  **Rif. Originale:** {r.get('Rif_Orig')}\n"
                    testo_risposta += f"  **Descrizione:** {r.get('Descrizione', 'N/D')}\n"
                    if pd.notna(r.get('Modelli_Compatibilita')) and str(r.get('Modelli_Compatibilita')) != '':
                        testo_risposta += f"  **Compatibilità/Dettagli:** {r.get('Modelli_Compatibilita')}\n"
                    testo_risposta += "\n"
            else:
                testo_risposta = "Non ho trovato questo ricambio esatto nel catalogo."
                
            st.markdown(testo_risposta)
            
    st.session_state.messages.append({"role": "assistant", "content": testo_risposta})

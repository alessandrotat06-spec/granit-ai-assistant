import streamlit as st
import pandas as pd
from google import genai

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Granit AI Assistant", page_icon="🚜", layout="centered")

st.title("🚜 Granit Quality Parts - Assistente IA")
st.write("Chiedi informazioni sui ricambi e naviga il catalogo in modo istantaneo.")

# Configurazione della chiave API di Google con la nuova libreria
client = genai.Client(api_key="AQ.Ab8RN6JavzpWb7CgSW_1z7AYBuLUMP5UQ8KTcye9Xh28Tg_hFg")

# Caricamento del catalogo CSV
@st.cache_data
def carica_catalogo():
    try:
        df = pd.read_csv('catalogo_granit.csv')
        return df.to_string(index=False)
    except Exception as e:
        return "Catalogo non trovato."

catalogo_testo = carica_catalogo()

# Configurazione delle istruzioni di sistema per il modello
system_prompt = f"""
Sei l'assistente virtuale ufficiale di Granit Quality Parts.
ECCO IL CATALOGO COMPLETO DEI PRODOTTI:
{catalogo_testo}

REGOLE TASSATIVE:
1. Rispondi usando ESCLUSIVAMENTE i dati presenti nel catalogo sopra.
2. Sii diretto, professionale e veloce.
3. Se un ricambio non è presente nel catalogo, di' chiaramente che non è disponibile.
"""

# Gestione della cronologia della chat nell'interfaccia di Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input dell'utente
if user_query := st.chat_input("Cerca un ricambio o fai una domanda..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Sto cercando nel catalogo..."):
            try:
                # Chiamata pulita e moderna all'API di Gemini
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_query,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.2,
                    ),
                )
                testo_risposta = response.text
            except Exception as e:
                testo_risposta = f"Errore di connessione con l' IA: {e}"
                
            st.markdown(testo_risposta)
            
    st.session_state.messages.append({"role": "assistant", "content": testo_risposta})

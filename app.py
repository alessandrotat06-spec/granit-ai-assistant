import streamlit as st
import pandas as pd
from google import genai

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Granit Quality Parts - Assistente IA", page_icon="🚜", layout="centered")

st.title("🚜 Granit Quality Parts - Assistente IA")
st.write("Chiedi informazioni sui ricambi e naviga il catalogo ufficiale con l'intelligenza artificiale.")

# Caricamento del catalogo CSV
@st.cache_data
def carica_catalogo():
    try:
        df = pd.read_csv('catalogo_granit.csv')
        return df.to_string(index=False)
    except Exception as e:
        return "Catalogo non trovato."

catalogo_testo = carica_catalogo()

# Gestione della cronologia chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input dell'utente
if user_query := st.chat_input("Cerca un ricambio (es. cuneo freno, staffa a u, anello in gomma)..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("L'intelligenza artificiale sta cercando nel catalogo..."):
            try:
                # Inserisci qui la tua chiave API di Google tra le virgolette
                client = genai.Client(api_key="AQ.Ab8RN6JavzpWb7CgSW_1z7AYBuLUMP5UQ8KTcye9Xh28Tg_hFg")
                
                system_prompt = f"""
Sei l'assistente virtuale ufficiale di Granit Quality Parts.
ECCO IL CATALOGO COMPLETO DEI PRODOTTI:
{catalogo_testo}

REGOLE TASSATIVE:
1. Rispondi usando ESCLUSIVAMENTE i dati presenti nel catalogo sopra. Non inventare codici o prodotti che non sono scritti nel catalogo.
2. Sii diretto e preciso. Quando un utente cerca un ricambio (es. cuneo freno, staffa a u, ecc.), restituisci il prodotto corrispondente esatto con il suo Codice Articolo, Rif. Originale, Descrizione e Compatibilità/Dettagli.
3. Se il ricambio richiesto non è presente nel catalogo, di' chiaramente: "Non ho trovato questo ricambio nel catalogo."
4. Non inserire prodotti a caso che non c'entrano nulla con la ricerca dell'utente.
"""

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_query,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.0,
                    ),
                )
                testo_risposta = response.text
            except Exception as e:
                testo_risposta = f"Si è verificato un errore durante la connessione con l'IA di Google: {e}"
            
            st.markdown(testo_risposta)
            st.session_state.messages.append({"role": "assistant", "content": testo_risposta})

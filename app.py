import streamlit as st
import pandas as pd
from google import genai

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Granit AI Assistant", page_icon="🚜", layout="centered")

st.title("🚜 Granit Quality Parts - Assistente IA")
st.write("Chiedi informazioni sui ricambi e naviga il catalogo in modo istantaneo.")

# Configurazione della chiave API di Google
client = genai.Client(api_key="AQ.Ab8RN6JavzpWb7CgSW_1z7AYBuLUMP5UQ8KTcye9Xh28Tg_hFg")

# Caricamento del catalogo CSV
@st.cache_data
def carica_catalogo():
    try:
        df = pd.read_csv('catalogo_granit.csv')
        return df, df.to_string(index=False)
    except Exception as e:
        return None, "Catalogo non trovato."

df_catalogo, catalogo_testo = carica_catalogo()

system_prompt = f"""
Sei l'assistente virtuale ufficiale di Granit Quality Parts.
ECCO IL CATALOGO COMPLETO DEI PRODOTTI:
{catalogo_testo}

REGOLE TASSATIVE:
1. Rispondi usando ESCLUSIVAMENTE i dati presenti nel catalogo sopra.
2. Sii diretto, professionale e veloce.
3. Se un ricambio non è presente nel catalogo, di' chiaramente che non è disponibile.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query := st.chat_input("Cerca un ricambio o fai una domanda..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Sto cercando nel catalogo..."):
            testo_risposta = None
            try:
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=user_query,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.2,
                    ),
                )
                testo_risposta = response.text
            except Exception as e:
                # Se becchi il limite della quota (429) o sovraccarico (503), 
                # facciamo una ricerca di sicurezza nel DataFrame per non bloccare la demo!
                query_lower = user_query.lower()
                risultati_trovati = []
                if df_catalogo is not None:
                    for index, row in df_catalogo.iterrows():
                        row_str = " ".join(str(val).lower() for val in row.values)
                        if any(parola in row_str for parola in query_lower.split() if len(parola) > 2):
                            risultati_trovati.append(str(row.values))
                
                if risultati_trovati:
                    testo_risposta = f"*(Nota: I server Google sono temporaneamente limitati in frequenza, ma ecco cosa ho trovato direttamente nel catalogo)*:\n\n" + "\n".join(risultati_trovati[:3])
                else:
                    testo_risposta = f"Al momento i server di Google hanno raggiunto il limite massimo di richieste gratuite (Errore 429/Quota). Aspetta un minuto oppure controlla i dati nel catalogo."
                
            st.markdown(testo_risposta)
            
    st.session_state.messages.append({"role": "assistant", "content": testo_risposta})

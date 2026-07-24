import streamlit as st
import pandas as pd
from google import genai

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Granit Quality Parts - Assistente IA", page_icon="🚜", layout="centered")

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
3. Se un utente cerca un ricambio, restituisci ESCLUSIVAMENTE il prodotto corrispondente esatto. Non inventare abbinamenti e non mostrare altri pezzi a caso.
4. Se il ricambio non è presente nel catalogo, di' chiaramente che non è disponibile.
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
                        temperature=0.0,
                    ),
                )
                testo_risposta = response.text
            except Exception as e:
                # Ricerca di riserva precisa sul CSV
                query_lower = user_query.lower()
                righe_trovate = []
                
                if df_catalogo is not None:
                    parole_chiave = [p for p in query_lower.split() if len(p) > 2]
                    for index, row in df_catalogo.iterrows():
                        row_str = " ".join(str(val).lower() for val in row.values)
                        if any(parola in row_str for parola in parole_chiave):
                            righe_trovate.append(row)
                
                if righe_trovate:
                    testo_risposta = "Ecco il ricambio trovato nel catalogo:\n\n"
                    for r in righe_trovate[:3]:
                        valori = list(r.values)
                        codice = valori[0] if len(valori) > 0 else ""
                        descrizione = valori[2] if len(valori) > 2 else (valori[1] if len(valori) > 1 else "")
                        compatibilita = valori[3] if len(valori) > 3 else ""
                        
                        testo_risposta += f"- **Codice Articolo:** {codice}\n"
                        testo_risposta += f"  **Descrizione:** {descrizione}\n"
                        if compatibilita:
                            testo_risposta += f"  **Compatibilità/Dettagli:** {compatibilita}\n"
                        testo_risposta += "\n"
                else:
                    testo_risposta = "Non ho trovato questo ricambio esatto nel catalogo."
                
            st.markdown(testo_risposta)
            
    st.session_state.messages.append({"role": "assistant", "content": testo_risposta})

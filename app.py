import streamlit as st
import pandas as pd

st.set_page_config(page_title="Granit Quality Parts - Assistente IA", page_icon="🚜", layout="centered")

st.title("🚜 Granit Quality Parts - Assistente IA")
st.write("Cerca i ricambi nel catalogo ufficiale in modo istantaneo.")

@st.cache_data
def carica_catalogo():
    try:
        return pd.read_csv('catalogo_granit.csv')
    except:
        return None

df_catalogo = carica_catalogo()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query := st.chat_input("Cerca un ricambio..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Sto cercando nel catalogo..."):
            risultati_esatti = []
            risultati_simili = []
            
            if df_catalogo is not None:
                query_lower = user_query.lower()
                parole_query = [p for p in query_lower.split() if len(p) > 1]
                
                for _, row in df_catalogo.iterrows():
                    descrizione = str(row.get('Descrizione', '')).lower()
                    codice = str(row.get('Codice', '')).lower()
                    rif = str(row.get('Rif_Orig', '')).lower()
                    riga_testo = f"{codice} {rif} {descrizione} {str(row.get('Modelli_Compatibilita', '')).lower()}"
                    
                    # Priorità massima: se la descrizione contiene tutte le parole chiave principali (es. "staffa" e "u")
                    if all(p in descrizione for p in parole_query):
                        risultati_esatti.append(row)
                    elif any(p in riga_testo for p in parole_query):
                        risultati_simili.append(row)

            # Uniamo mettendo prima i risultati esatti
            tutti_risultati = risultati_esatti + [r for r in risultati_simili if r not in risultati_esatti]

            if tutti_risultati:
                testo_risposta = "Ecco i ricambi trovati nel catalogo ufficiale:\n\n"
                for r in tutti_risultati[:5]:
                    testo_risposta += f"- **Codice Articolo:** {r.get('Codice', 'N/D')}\n"
                    if pd.notna(r.get('Rif_Orig')) and str(r.get('Rid_Orig')) != '':
                        testo_risposta += f"  **Rif. Originale:** {r.get('Rif_Orig')}\n"
                    testo_risposta += f"  **Descrizione:** {r.get('Descrizione', 'N/D')}\n"
                    if pd.notna(r.get('Modelli_Compatibilita')) and str(r.get('Modelli_Compatibilita')) != '':
                        testo_risposta += f"  **Compatibilità/Dettagli:** {r.get('Modelli_Compatibilita')}\n"
                    testo_risposta += "\n"
            else:
                testo_risposta = "Non ho trovato questo ricambio esatto nel catalogo."
                
            st.markdown(testo_risposta)
            
    st.session_state.messages.append({"role": "assistant", "content": testo_risposta})

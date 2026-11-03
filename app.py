import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

st.set_page_config(page_title="Tutor HSK4", page_icon="🇨🇳")
st.title("Tutor Virtuale HSK 4")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chiave API mancante.")
    st.stop()

# Funzione per leggere automaticamente tutti i PDF nascosti nel sistema
@st.cache_data
def load_knowledge():
    text = ""
    # Cerca tutti i file PDF nella cartella di GitHub
    for filename in os.listdir('.'):
        if filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(filename)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    return text

pdf_text = load_knowledge()

if not pdf_text:
    st.warning("Sto attendendo i materiali di studio. Il docente li caricherà a breve!")
else:
    st.success("Tutti i materiali HSK 4 sono caricati e attivi. Iniziamo!")

# Inizializza la chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input studente
if prompt := st.chat_input("Scrivi qui la tua risposta o domanda..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Le istruzioni del tutor
    system_instruction = f"""
    Sei un tutor universitario esperto per l'esame di lingua cinese HSK 4. 
    Il tuo compito è interrogare lo studente sui materiali forniti e correggerlo.
    Se sbaglia un carattere o un vocabolo, non dare solo la traduzione: scomponi i radicali, analizza l'etimologia o proponi associazioni visive per agevolare il recupero mnemonico.
    Mantieni un tono incoraggiante e rigoroso.
    Ecco la tua base di conoscenza: {pdf_text}
    """
    
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest', system_instruction=system_instruction)
    chat_history = [{"role": m["role"] if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
    
    chat = model.start_chat(history=chat_history)
    response = chat.send_message(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})

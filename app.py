import streamlit as st
import google.generativeai as genai
import PyPDF2

st.set_page_config(page_title="Tutor HSK4", page_icon="🇨🇳")
st.title("Tutor Virtuale HSK 4")

# Configura l'API di Gemini in modo sicuro
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Chiave API non trovata. Configura i Secrets su Streamlit.")
    st.stop()

# Caricamento del PDF
st.sidebar.header("Materiali di Studio")
uploaded_file = st.sidebar.file_uploader("Carica qui il tuo PDF HSK 4", type="pdf")
pdf_text = ""

if uploaded_file is not None:
    reader = PyPDF2.PdfReader(uploaded_file)
    for page in reader.pages:
        pdf_text += page.extract_text() + "\n"
    st.sidebar.success("PDF caricato e letto con successo!")

# Inizializza la cronologia della chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input dell'utente (studente)
if prompt := st.chat_input("Scrivi la tua risposta o fai una domanda..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Prompt di sistema personalizzato (puoi modificarlo in seguito per aggiungere le tue mnemotecniche)
    system_instruction = f"""
    Sei un tutor universitario esperto per l'esame di lingua cinese HSK 4. 
    Il tuo compito è interrogare lo studente sui materiali caricati e correggerlo.
    Se sbaglia, non dare solo la soluzione, ma spiega la regola o la composizione del carattere/radicale.
    Ecco il materiale di riferimento estratto dal PDF: {pdf_text}
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
    
    # Genera la risposta passando la cronologia
    chat_history = [{"role": m["role"] if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
    
    chat = model.start_chat(history=chat_history)
    response = chat.send_message(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
  

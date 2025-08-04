# app.py

import streamlit as st
import os
from config import APP_TITLE, APP_ICON, DATA_DIR, VERSION, DEVELOPER
from utils.loader import load_pdf_vectorstore
from utils.chain import create_retrieval_chain
from utils.tts import generate_and_get_audio_path

# Set page configuration
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON)

# Sidebar UI
with st.sidebar:
    st.title(APP_TITLE)
    st.markdown("### **🔍 Features**")
    st.markdown("- Upload a **Research Paper** 📄")
    st.markdown("- Ask **questions** 🤖")
    st.markdown("- Get **instant answers** ⚡")

    st.markdown("---")
    st.subheader("⚙️ **Settings**")
    dark_mode = st.checkbox("🌙 Enable Dark Mode")
    temperature = st.slider("🎛 Set Answer Randomness (Temperature)", 0.0, 1.0, 0.7, 0.1)

    st.markdown("---")
    st.info(f"Developed by **{DEVELOPER}**", icon="💡")
    st.caption(f"📌 Version: {VERSION}")

# Main UI
st.title(APP_TITLE)
st.caption("Upload a Research Paper and start chatting!")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file:
    pdf_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    vector_store = load_pdf_vectorstore(pdf_path)
    retrieval_chain = create_retrieval_chain(vector_store, temperature)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Ask me questions about the PDF document..."}
        ]

    prompt = st.chat_input("Your question")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    question = st.session_state.messages[-1]["content"]
                    response = retrieval_chain({
                        "question": question,
                        "chat_history": [(msg["role"], msg["content"])
                                         for msg in st.session_state.messages
                                         if msg["role"] != "assistant"]
                    })

                    answer = response['answer']
                    st.write(answer)

                    # TTS
                    audio_path = generate_and_get_audio_path(answer)
                    with open(audio_path, "rb") as audio_file:
                        st.audio(audio_file.read(), format="audio/mp3")

                    st.session_state.messages.append({"role": "assistant", "content": answer})

                    if 'source_documents' in response:
                        with st.expander("View Source Documents"):
                            for i, doc in enumerate(response['source_documents']):
                                st.write(f"Source {i + 1}:")
                                st.write(doc.page_content)
                                st.write("---")

                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                    st.exception(e)

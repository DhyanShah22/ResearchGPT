import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from gtts import gTTS
from io import BytesIO
import tempfile
import openai

# Set OpenAI API Key (for Whisper)
# openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")

# Transcribe audio using OpenAI Whisper API
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

# Text-to-speech using gTTS (streamed)
def speak(text):
    tts = gTTS(text)
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    st.audio(audio_fp, format="audio/mp3")

st.set_page_config(page_title="ResearchGPT 🔬🤖", page_icon="📚")

# Sidebar UI
with st.sidebar:
    st.title("📌 ResearchGPT 🔬🤖")
    st.markdown("### **🔍 Features**")
    st.markdown("- Upload a **Research Paper** 📄")
    st.markdown("- Ask **questions** 🤖")
    st.markdown("- Get **instant answers** ⚡")

    st.markdown("---")
    st.subheader("⚙️ **Settings**")
    dark_mode = st.checkbox("🌙 Enable Dark Mode")
    if dark_mode:
        st.markdown(
            """<style>body { background-color: #0E1117; color: white; }</style>""",
            unsafe_allow_html=True,
        )

    temperature = st.slider("🎛 Set Answer Randomness (Temperature)", 0.0, 1.0, 0.7, 0.1)
    st.markdown("---")
    st.info("Developed by **Dhyan Shah**", icon="💡")
    st.caption("📌 Version: 1.0.0")

# Gemini API key
GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"

# Data directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Step 1: Upload PDF
st.title("ResearchGPT 🔬🤖")
st.caption("Upload a Research Paper and start chatting!")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file:
    pdf_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded: {uploaded_file.name}")

# Voice Input
st.markdown("🎤 **Optional: Use Voice to Ask a Question**")

audio_bytes = st.file_uploader("Upload voice query (MP3/WAV)", type=["mp3", "wav"])
voice_text = None

if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tmpfile.write(audio_bytes.read())
        tmpfile_path = tmpfile.name

    st.info("🔍 Transcribing voice...")
    try:
        voice_text = transcribe_audio(tmpfile_path)
        st.success(f"🗣️ Transcribed: {voice_text}")
    except Exception as e:
        st.error("❌ Transcription failed.")
        st.exception(e)

# Load and Process PDF
@st.cache_resource(show_spinner=False)
def load_data(pdf_path):
    with st.spinner("Loading and indexing the document..."):
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        if not documents:
            st.error("❌ Could not load the PDF document!")
            st.stop()

        st.success(f"✅ Loaded PDF with {len(documents)} pages")

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GEMINI_API_KEY
        )

        vector_store = FAISS.from_documents(documents, embeddings)
        st.success("✅ Successfully created vector store!")

        return vector_store

# Initialize Retrieval Chain
if uploaded_file:
    vector_store = load_data(pdf_path)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        return_messages=True
    )

    chat_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=GEMINI_API_KEY,
        temperature=temperature,
        convert_system_message_to_human=True
    )

    retrieval_chain = ConversationalRetrievalChain.from_llm(
        llm=chat_model,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True,
        chain_type="stuff",
        verbose=True
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Ask me questions about the PDF document..."}
        ]

    prompt = st.chat_input("Your question")

    if voice_text and not prompt:
        st.info(f"Using transcribed voice input: **{voice_text}**")
        prompt = voice_text

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Process Input
    if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    question = st.session_state.messages[-1]["content"]
                    response = retrieval_chain({
                        "question": question,
                        "chat_history": [
                            (msg["role"], msg["content"])
                            for msg in st.session_state.messages if msg["role"] != "assistant"
                        ]
                    })

                    answer = response.get("answer", "I'm not sure how to answer that.")
                    st.write(answer)
                    speak(answer)

                    st.session_state.messages.append({"role": "assistant", "content": answer})

                    if 'source_documents' in response:
                        with st.expander("View Source Documents"):
                            for i, doc in enumerate(response['source_documents']):
                                st.write(f"Source {i+1}:")
                                st.write(doc.page_content)
                                st.write("---")

                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                    st.exception(e)

import os
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from gtts import gTTS
import base64

# Set page config
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
    temperature = st.slider("🎛 Set Answer Randomness (Temperature)", 0.0, 1.0, 0.7, 0.1)

    st.markdown("---")
    st.info("Developed by **Dhyan Shah**", icon="💡")
    st.caption("📌 Version: 1.0.0")

# Set up API Key
# GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"

# Create data directory
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Upload PDF
st.title("ResearchGPT 🔬🤖")
st.caption("Upload a Research Paper and start chatting!")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file:
    pdf_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded: {uploaded_file.name}")

# Load and process PDF
@st.cache_resource(show_spinner=False)
def load_data(pdf_path):
    try:
        with st.spinner("Loading and indexing the document..."):
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()

            if not documents:
                st.error("❌ Could not load the PDF document!")
                st.stop()

            st.success(f"✅ Loaded PDF with {len(documents)} pages")

            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=GEMINI_API_KEY,
                credentials=None
            )

            vector_store = FAISS.from_documents(documents, embeddings)
            st.success("✅ Successfully created vector store!")
            return vector_store
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()

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
        credentials=None,
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

    # Initialize chat state
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

                    # ✅ Text-to-Speech here
                    tts = gTTS(text=answer, lang='en')
                    audio_path = os.path.join(DATA_DIR, "response.mp3")
                    tts.save(audio_path)

                    # Play audio using Streamlit's built-in audio function
                    with open(audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format="audio/mp3")

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

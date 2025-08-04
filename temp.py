import os
import re
import streamlit as st
from gtts import gTTS
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from auth import login_form, signup_form
from db import create_users_table, create_documents_table, create_chat_table, log_document, log_chat, delete_chat_history, create_chat_sessions_table

# -----------------🔧 Configuration --------------------
st.set_page_config(page_title="ResearchGPT 🔬🤖", page_icon="📚")

# Setup database tables
create_users_table()
create_documents_table()
create_chat_sessions_table()
create_chat_table()

# Session state initialization
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("name", "")
st.session_state.setdefault("messages", [
    {"role": "assistant", "content": "Ask me questions about the PDF document..."}
])
st.session_state.setdefault("save_chat", True)

# -----------------🔒 Auth UI -------------------------
if not st.session_state.authenticated:
    st.sidebar.title("👋 Welcome")
    auth_mode = st.sidebar.radio("Choose", ["Login", "Sign Up"], index=1)
    (login_form if auth_mode == "Login" else signup_form)()
    st.stop()
else:
    st.sidebar.success(f"✅ Logged in as {st.session_state.name}")
    if st.sidebar.button("🚪 Logout"):
        if not st.session_state.save_chat:
            delete_chat_history(st.session_state.name)
        st.session_state.update({"authenticated": False})
        st.rerun()

st.sidebar.markdown("---")

# -----------------🧠 Sidebar UI ----------------------
st.sidebar.title("📌 ResearchGPT 🔬🤖")
st.sidebar.markdown("### **🔍 Features**")
st.sidebar.markdown("- Upload a **Research Paper** 📄")
st.sidebar.markdown("- Ask **questions** 🤖")
st.sidebar.markdown("- Get **instant answers** ⚡")

st.sidebar.subheader("⚙️ Settings")
dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode")
temperature = st.sidebar.slider("🎛 Answer Randomness", 0.0, 1.0, 0.7, 0.1)
st.session_state.save_chat = st.sidebar.radio("💾 Save Chat History?", ["Yes", "No"]) == "Yes"

st.sidebar.info("Developed by **Dhyan Shah**", icon="💡")
st.sidebar.caption("📌 Version: 2.0.0")

# -----------------🔐 API Key -------------------------
GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"

# -----------------📂 Upload UI ------------------------
st.title("ResearchGPT 🔬🤖")
st.caption(f"Welcome, {st.session_state.name}! Upload a Research Paper and start chatting!")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

uploaded_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])
pdf_path = None

if uploaded_file:
    pdf_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded: {uploaded_file.name}")
    log_document(st.session_state.name, uploaded_file.name)

# -----------------📚 Load PDF into Vector Store ---------------------
@st.cache_resource(show_spinner=False)
def load_data(path):
    loader = PyPDFLoader(path)
    documents = loader.load()

    if not documents:
        st.error("❌ Could not load the PDF document!")
        st.stop()

    st.success(f"✅ Loaded PDF with {len(documents)} pages")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY
    )
    return FAISS.from_documents(documents, embeddings)

# -----------------🤖 Chatbot Engine -------------------
if pdf_path:
    vector_store = load_data(pdf_path)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    chat_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=temperature,
        google_api_key=GEMINI_API_KEY,
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

    prompt = st.chat_input("💬 Ask a question about the PDF...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        if st.session_state.save_chat:
            log_chat(st.session_state.name, "user", prompt)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    question = st.session_state.messages[-1]["content"]
                    response = retrieval_chain({
                        "question": question,
                        "chat_history": [
                            (m["role"], m["content"]) for m in st.session_state.messages if m["role"] != "assistant"
                        ]
                    })

                    answer = response["answer"]
                    st.write(answer)

                    # ✅ Text to Speech
                    clean_answer = re.sub(r"[*_`#>\-]+", "", answer)
                    tts = gTTS(text=clean_answer, lang='en')
                    audio_path = os.path.join(DATA_DIR, "response.mp3")
                    tts.save(audio_path)

                    with open(audio_path, "rb") as f:
                        st.audio(f.read(), format="audio/mp3")

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    if st.session_state.save_chat:
                        log_chat(st.session_state.name, "assistant", answer)

                    if response.get("source_documents"):
                        with st.expander("📚 View Sources"):
                            for i, doc in enumerate(response["source_documents"]):
                                st.markdown(f"**Source {i+1}:**")
                                st.write(doc.page_content)
                                st.markdown("---")

                except Exception as e:
                    st.error("🚨 An error occurred while processing your request.")
                    st.exception(e)

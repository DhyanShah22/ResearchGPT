import os
import re
import requests
import streamlit as st
from gtts import gTTS
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import PyPDFLoader
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# ------------------------ Config ------------------------
st.set_page_config(page_title="ResearchGPT 🔬🤖", page_icon="📚")
GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ------------------------ Sidebar ------------------------
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
    st.caption("📌 Version: 2.0.0")

# ------------------------ Utility Functions ------------------------
def extract_references(text):
    pattern = r"(?i)(references|bibliography)\s*(.*?)$"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        raw_refs = match.group(2)
        references = re.split(r"\n\d+\.\s|\n•\s|\n\[.*?\]\s", raw_refs)
        return [ref.strip() for ref in references if len(ref.strip()) > 30]
    return []

def search_paper_semantic_scholar(title):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={title}&limit=1&fields=title,url,openAccessPdf"
    response = requests.get(url)
    data = response.json()
    if data.get("data"):
        paper = data["data"][0]
        return paper.get("openAccessPdf", {}).get("url")
    return None

@st.cache_resource(show_spinner=False)
def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_API_KEY
    )
    return FAISS.from_documents(documents, embeddings), documents

# ------------------------ Main Application ------------------------
st.title("ResearchGPT 🔬🤖")
st.caption("Upload a Research Paper and start chatting!")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    pdf_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    vector_store, original_docs = process_pdf(pdf_path)
    full_text = "\n".join([doc.page_content for doc in original_docs])
    references = extract_references(full_text)

    if "references" not in st.session_state:
        st.session_state.references = {}

    with st.spinner("🔍 Fetching and processing referenced papers..."):
        for ref in references:
            if ref not in st.session_state.references:
                try:
                    pdf_url = search_paper_semantic_scholar(ref)
                    if pdf_url:
                        pdf_data = requests.get(pdf_url)
                        ref_filename = re.sub(r"[^\w\s-]", "", ref[:50]) + ".pdf"
                        ref_path = os.path.join(DATA_DIR, ref_filename)
                        with open(ref_path, "wb") as f:
                            f.write(pdf_data.content)
                        vs, _ = process_pdf(ref_path)
                        st.session_state.references[ref] = vs
                except Exception as e:
                    st.warning(f"Skipping a reference due to error: {e}")

    selected_title = None
    if st.session_state.references:
        st.sidebar.subheader("📑 Referenced Papers")
        selected_title = st.sidebar.selectbox(
            "Select a referenced paper to chat with:",
            ["Main Uploaded Paper"] + list(st.session_state.references.keys())
        )

    memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)
    chat_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=GEMINI_API_KEY,
        temperature=temperature,
        convert_system_message_to_human=True
    )

    if selected_title and selected_title != "Main Uploaded Paper":
        active_vectorstore = st.session_state.references[selected_title]
    else:
        active_vectorstore = vector_store

    retrieval_chain = ConversationalRetrievalChain.from_llm(
        llm=chat_model,
        retriever=active_vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True,
        chain_type="stuff",
        verbose=True
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Ask me questions about the document..."}
        ]

    prompt = st.chat_input("Your question")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    question = st.session_state.messages[-1]["content"]
                    response = retrieval_chain({
                        "question": question,
                        "chat_history": [(m["role"], m["content"]) for m in st.session_state.messages if m["role"] != "assistant"]
                    })
                    answer = response['answer']
                    st.write(answer)

                    # Text-to-Speech
                    clean_text = re.sub(r"[*_`#>\-]+", "", answer)
                    tts = gTTS(text=clean_text, lang='en')
                    audio_path = os.path.join(DATA_DIR, "response.mp3")
                    tts.save(audio_path)

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
                    st.error(f"Error: {str(e)}")

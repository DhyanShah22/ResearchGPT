import os
import re
import requests
import streamlit as st
import fitz  # PyMuPDF for extracting references
import networkx as nx
import matplotlib.pyplot as plt
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Streamlit Config
st.set_page_config(page_title="ResearchGPT 🔬🤖", page_icon="📚")

# Sidebar Styling
with st.sidebar:
    st.title("📌 ResearchGPT 🔬🤖")
    st.markdown("### **🔍 Features**")
    st.markdown("- Upload a **Research Paper** 📄")
    st.markdown("- Retrieve **Citations & References** 🔗")
    st.markdown("- Explore **Related Research Papers** 📑")
    st.markdown("- Ask **questions** 🤖")
    st.markdown("- Get **instant answers** ⚡")

    st.markdown("---")
    
    st.subheader("⚙️ **Settings**")
    dark_mode = st.checkbox("🌙 Enable Dark Mode")
    temperature = st.slider("🎛 Set Answer Randomness (Temperature)", 0.0, 1.0, 0.7, 0.1)

    st.markdown("---")
    st.info("Developed by **Dhyan Shah**", icon="💡")
    st.caption("📌 Version: 2.0.0")

# Set up API Key
GEMINI_API_KEY = "AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys"
# GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Define data directory
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# **🔹 Step 1: Upload PDF File**
st.title("ResearchGPT 🔬🤖")
st.caption("Upload a Research Paper and start chatting!")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file:
    pdf_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())  # Save the uploaded file
    st.success(f"✅ Uploaded: {uploaded_file.name}")

# **🔹 Step 2: Extract References from PDF**
def extract_references(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    # Extract all text from the document
    for page in doc:
        full_text += page.get_text("text") + "\n"

    # Locate the References section
    ref_start = re.search(r"\bReferences\b|\bBibliography\b|\bWorks Cited\b", full_text, re.IGNORECASE)
    if ref_start:
        ref_text = full_text[ref_start.start():]  # Extract text after "References"
    else:
        ref_text = full_text  # If no "References" found, use entire text (fallback)

    # Improved regex patterns to capture different reference formats
    reference_patterns = [
        re.compile(r"\[\d+\]\s*(.+)"),  # IEEE-style references [1] Reference text
        re.compile(r"^\d+\.\s+(.+)", re.MULTILINE),  # Numbered references (1. Author, Title, Year)
        re.compile(r"\((.*?)\)\s*\d{4}"),  # APA-style inline citations (Author, Year)
        re.compile(r"([A-Z][a-z]+,?\s+[A-Z][a-z]+.*?\d{4})")  # General Author, Title, Year pattern
    ]

    references = []
    for pattern in reference_patterns:
        matches = pattern.findall(ref_text)
        references.extend(matches)

    return list(set(references))  # Remove duplicates

# **🔹 Step 3: Fetch Cited Papers (Using Semantic Scholar API)**
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"

def fetch_referenced_papers(title):
    response = requests.get(SEMANTIC_SCHOLAR_API, params={"query": title, "fields": "title,url"})
    if response.status_code == 200:
        data = response.json()
        return [(p["title"], p["url"]) for p in data.get("data", [])]
    return []

# **🔹 Step 4: Build Citation Tree Using DFS**
def build_citation_tree(root_paper, depth_limit=2):
    citation_graph = nx.DiGraph()
    stack = [(root_paper, 0)]
    
    while stack:
        paper, depth = stack.pop()
        if depth >= depth_limit:
            continue
        
        references = fetch_referenced_papers(paper)
        for ref_title, ref_url in references:
            citation_graph.add_edge(paper, ref_title, url=ref_url)
            stack.append((ref_title, depth + 1))

    return citation_graph

# **🔹 Step 5: Visualize Citation Graph**
def plot_citation_tree(graph):
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color="lightblue", edge_color="gray", font_size=8)
    st.pyplot(plt)

# **🔹 Step 6: Initialize Vector Store & Chat Model**
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
                google_api_key=GEMINI_API_KEY
            )

            vector_store = FAISS.from_documents(documents, embeddings)
            st.success("✅ Successfully created vector store!")

            return vector_store

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()

# **🔹 Step 7: Run Citation Retrieval & Chatbot**
if uploaded_file:
    vector_store = load_data(pdf_path)
    
    memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)
    chat_model = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=GEMINI_API_KEY,
        temperature=temperature
    )

    retrieval_chain = ConversationalRetrievalChain.from_llm(
        llm=chat_model,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True,
        chain_type="stuff",
        verbose=True
    )

    # Extract and Display References
    references = extract_references(pdf_path)
    st.subheader("📌 Extracted References")
    if references:
        for ref in references:
            st.write(f"- {ref}")
    else:
        st.warning("⚠ No valid references detected! Check extracted text format.")

    # Debugging: Show first 1000 characters of raw extracted text to check format
    with fitz.open(pdf_path) as doc:
        full_text = "\n".join([page.get_text("text") for page in doc])
    st.text_area("Raw Extracted Text (Debugging)", full_text[:2000])  # Increase to 2000 for better visibility



    # Build & Show Citation Tree
    if st.button("🔍 Retrieve Referenced Papers"):
        with st.spinner("Fetching referenced papers..."):
            citation_graph = build_citation_tree(uploaded_file.name)
            st.subheader("📌 Citation Tree")
            plot_citation_tree(citation_graph)

    # **Chat Interface**
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Ask me questions about the PDF document..."}]

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
                        "chat_history": [(msg["role"], msg["content"]) for msg in st.session_state.messages if msg["role"] != "assistant"]
                    })

                    st.write(response['answer'])
                    st.session_state.messages.append({"role": "assistant", "content": response['answer']})

                    if 'source_documents' in response:
                        with st.expander("View Source Documents"):
                            for i, doc in enumerate(response['source_documents']):
                                st.write(f"Source {i+1}: {doc.page_content}")

                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

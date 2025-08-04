# utils/loader.py

import os
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st
from config import GEMINI_API_KEY

@st.cache_resource(show_spinner=False)
def load_pdf_vectorstore(pdf_path):
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

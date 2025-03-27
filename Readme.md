ResearchGPT 🧠📚
AI-Powered Research Paper Assistant

🚀 ResearchGPT is an intelligent chatbot designed to help researchers, students, and professionals analyze research papers efficiently. By leveraging Retrieval-Augmented Generation (RAG), vector databases, and LLMs, it enables interactive, context-aware conversations with research papers.

🔹 Features
✅ Upload Research Papers – Easily upload PDFs and interact with them.
✅ Instant Insights – No need to skim through pages—just ask and get precise answers.
✅ Complex Concept Explanation – Breaks down difficult research topics into simple explanations.
✅ Reliable & Transparent – Every response is backed by original sources.
✅ Interactive & Context-Aware – Remembers past queries for a more natural conversation.

🛠️ Tech Stack
Frontend:
Streamlit 🖥️ – Provides an interactive UI for chatting with PDFs.

Backend:
Django 🕸️ – Manages API requests and handles document processing.

LangChain 🧠 – Enables interaction with LLMs and retrieval-based querying.

FAISS (Facebook AI Similarity Search) 📌 – Efficiently indexes and retrieves document embeddings.

Google Gemini AI 🤖 – Powers LLM responses and embeddings.

Storage & Data Handling:
Vector Database (FAISS) – Stores and retrieves document embeddings.

Conversation Memory (LangChain) – Maintains chat history for context-aware responses.

⚙️ APIs & Functionality
1️⃣ Upload & Process PDFs
Endpoint: POST /upload

Description: Accepts a PDF file and processes its content using PyPDFLoader.

Response: Returns metadata about the document.

2️⃣ Query Research Papers
Endpoint: POST /query

Description: Accepts a user question and retrieves relevant text from the PDF using FAISS.

Response: Provides an AI-generated response with references to the original document.

3️⃣ Retrieve Conversation History
Endpoint: GET /chat-history

Description: Returns previous interactions for context-aware discussions.

Response: List of past user queries and AI responses.

📦 Installation & Setup
1️⃣ Clone the Repository
bash
Copy
Edit
git clone https://github.com/your-username/ResearchGPT.git
cd ResearchGPT
2️⃣ Create a Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
3️⃣ Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4️⃣ Set Up Environment Variables
Create a .env file and add your Google Gemini API Key:

ini
Copy
Edit
GEMINI_API_KEY=your_google_api_key
5️⃣ Run the Application
bash
Copy
Edit
streamlit run app.py
The app will be available at http://localhost:8501.

📌 How It Works
1️⃣ Upload a Research Paper – The PDF is processed, and embeddings are generated.
2️⃣ Ask Questions – The chatbot retrieves relevant text using FAISS and LLMs.
3️⃣ Get Context-Aware Answers – The AI remembers your previous queries and provides intelligent responses.

🔮 Future Improvements
Support for Multiple File Uploads

Integration with More LLMs (GPT-4, Claude, etc.)

Multimodal Capabilities (Images, Graphs, etc.)

This project aims to revolutionize how researchers interact with academic papers—making research faster, smarter, and more accessible. 🚀

Contributions are welcome! Feel free to fork, improve, and submit PRs. 😊
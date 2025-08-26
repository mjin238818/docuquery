# DocuQuery

DocuQuery is a **Streamlit-based RAG (Retrieval-Augmented Generation) app** that lets you load knowledge from:
- 🔗 URLs  
- 📄 PDFs  
- ✍️ Custom text  

Once sources are added, you can ask natural language questions, and the app will provide answers along with references.

### 🚀 Features
- Upload multiple PDFs and fetch from URLs
- Paste your own text snippets for quick knowledge injection
- FAISS vector store for fast similarity search
- HuggingFace embeddings (`all-MiniLM-L6-v2`)
- Powered by Google Gemma LLM (via LangChain)

### 🛠 Installation

- git clone https://github.com/mjin238818/docuquery.git
- cd docuquery
- pip install -r requirements.txt

### ▶️ Usage

- streamlit run app.py

⚡ Ask questions like:

- *Summarize this PDF in 3 bullet points.*
- *What are the key takeaways from the provided articles?*

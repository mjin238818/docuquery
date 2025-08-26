import streamlit as st
import os
from dotenv import load_dotenv
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader, PyPDFLoader, TextLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import tempfile
from dotenv import load_dotenv
load_dotenv()
try:
    llm = ChatGoogleGenerativeAI(
        model="gemma-3n-e2b-it",  # Available in AI Studio
        temperature=0.7,
        google_api_key=os.environ["GOOGLE_API_KEY"]
    )
except:
    st.header("check llm")
st.title("Information QA BOT")
st.sidebar.title("Sources")
try:
    num_urls = st.sidebar.number_input("Enter number of URLs", min_value=0, step=1)
    urls = []
    for i in range(num_urls):
        url = st.sidebar.text_input(f"Enter URL {i+1}")
        if url:
            urls.append(url)
    # Upload PDFs
    uploaded_pdfs = st.sidebar.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
    # Upload text
    user_text = st.sidebar.text_area("Paste your text here", height=150)

except:
    st.subheader("Please provide Sources you want to research")

main_placefolder=st.empty()
proceed_clicked=st.sidebar.button("Proceed")
vectorstore_path = "faiss_index"
if proceed_clicked:
    docs = []
    # Load from URLs
    if urls:
        main_placefolder.text("🔗 Loading data from URLs...")
        loader = UnstructuredURLLoader(urls)
        docs.extend(loader.load())
        # Load from PDFs
    if uploaded_pdfs:
        for pdf_file in uploaded_pdfs:
            main_placefolder.text(f"📄 Loading {pdf_file.name}...")
            pdf_path = os.path.join("temp", pdf_file.name)
            os.makedirs("temp", exist_ok=True)
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            loader = PyPDFLoader(pdf_path)
            docs.extend(loader.load())

    if user_text.strip():
        main_placefolder.text("📝 Loading pasted text...")

        # Save pasted text to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp_file:
            tmp_file.write(user_text)
            tmp_path = tmp_file.name

        # Load using TextLoader
        loader = TextLoader(tmp_path, encoding="utf-8")
        docs.extend(loader.load())

    if not docs:
        st.error("No documents loaded. Please provide URLs or PDFs.")
        st.stop()

    #splitting into chunks
    chunk_splitter=RecursiveCharacterTextSplitter(
        separators=["\n\n","\n",".",","],
        chunk_size=1000,
        chunk_overlap=100
    )
    main_placefolder.text("Aura Farming...")
    docs = chunk_splitter.split_documents(docs)

    #create embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_db = FAISS.from_documents(docs, embeddings)
    vector_db.save_local(vectorstore_path)
    main_placefolder.text("... OMG!!! It's over 9000 ...")
# Load vectorstore and chain (if exists)
if os.path.exists(vectorstore_path):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(
        vectorstore_path,
        embeddings,
        allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever()

    # Create chain outside proceed_clicked
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="map_reduce"
    )

    # Query input
    query = st.text_input("Ask a question:")
    if st.button("Submit") and query:
        result = chain({"question": query}, return_only_outputs=True)
        st.subheader("Answer")
        st.write(result["answer"])
        st.subheader("Sources")
        st.write(result.get("sources"))
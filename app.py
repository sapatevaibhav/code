import os
import streamlit as st
import google.generativeai as genai
from code_indexer import index_files, process_file
from rag_engine import CodeRAG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if API key is set
if not os.getenv("GEMINI_API_KEY"):
    st.error("GEMINI_API_KEY not found in environment variables. Please set it up.")
    st.stop()

# Set up session state
if 'rag' not in st.session_state:
    st.session_state.rag = CodeRAG()

if 'indexed_files' not in st.session_state:
    st.session_state.indexed_files = []

def index_uploaded_files(uploaded_files):
    """Process uploaded files and add to index"""
    if not uploaded_files:
        return

    temp_file_paths = []

    # Save uploaded files temporarily
    for uploaded_file in uploaded_files:
        file_path = os.path.join("./temp", uploaded_file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        temp_file_paths.append(file_path)
        st.session_state.indexed_files.append(uploaded_file.name)

    # Index files
    code_elements = index_files(temp_file_paths)

    # Add to vector database
    if code_elements:
        st.session_state.rag.add_documents(code_elements)
        st.success(f"Successfully indexed {len(temp_file_paths)} files")

# App title and description
st.title("Code RAG Assistant")
st.markdown("Upload code files and ask questions about them")

# File upload section
with st.sidebar:
    st.header("Upload Files")
    uploaded_files = st.file_uploader(
        "Upload code files",
        accept_multiple_files=True,
        type=["py", "js", "ts", "java", "c", "cpp", "h", "hpp", "cs", "go", "rb", "php", "html", "css" ,"txt"]
    )

    if st.button("Index Files"):
        with st.spinner("Indexing files..."):
            index_uploaded_files(uploaded_files)

    st.header("Indexed Files")
    if st.session_state.indexed_files:
        for file in st.session_state.indexed_files:
            st.text(f"- {file}")
    else:
        st.info("No files indexed yet")

# Query section
st.header("Ask a Question")
query = st.text_area("Enter your question about the code:")

if st.button("Get Answer"):
    if not st.session_state.indexed_files:
        st.warning("Please upload and index files first.")
    elif not query:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating response..."):
            response = st.session_state.rag.process_query(query)
            st.markdown("### Answer")
            st.markdown(response)

# # Environment setup instructions
# with st.sidebar:
#     st.header("Setup Instructions")
#     st.markdown("""
#     1. Create a `.env` file in the project root
#     2. Add your Gemini API key: `GEMINI_API_KEY=your_key_here`
#     3. Restart the app
#     """)

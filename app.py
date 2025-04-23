import os
import shutil
import streamlit as st
import google.generativeai as genai
import atexit
from code_indexer import index_files, process_file
from rag_engine import CodeRAG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define temp directory
TEMP_DIR = "./temp"
DATA_DIR = "./data"

def cleanup_temp_files():
    """Clean up temporary files"""
    if os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
            print(f"Cleaned up temporary files in {TEMP_DIR}")
        except Exception as e:
            print(f"Error cleaning up temp files: {str(e)}")

# Register cleanup function to run on exit
atexit.register(cleanup_temp_files)

# Create temp directory if it doesn't exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Check if API key is set
if not os.getenv("GEMINI_API_KEY"):
    st.error("GEMINI_API_KEY not found in environment variables. Please set it up.")
    st.stop()

# Set up session state
if 'rag' not in st.session_state:
    st.session_state.rag = CodeRAG(persist_directory=DATA_DIR)

if 'indexed_files' not in st.session_state:
    st.session_state.indexed_files = []

if 'last_files_hash' not in st.session_state:
    st.session_state.last_files_hash = ""

def index_uploaded_files(uploaded_files):
    """Process uploaded files and add to index"""
    if not uploaded_files:
        return False

    # Clean up the temp directory before adding new files
    cleanup_temp_files()
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Clear existing indexed files
    st.session_state.rag.clear_collection()
    st.session_state.indexed_files = []

    temp_file_paths = []

    # Save uploaded files temporarily
    for uploaded_file in uploaded_files:
        file_path = os.path.join(TEMP_DIR, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        temp_file_paths.append(file_path)
        st.session_state.indexed_files.append(uploaded_file.name)

    # Index files
    code_elements = index_files(temp_file_paths)

    # Add to vector database
    if code_elements:
        st.session_state.rag.add_documents(code_elements)
        return True

    return False

def get_files_hash(files):
    """Create a hash of file names and modified times to detect changes"""
    if not files:
        return ""
    return "-".join(sorted([f"{file.name}_{file.size}" for file in files]))

# App title and description
st.title("Code RAG Assistant")
st.markdown("Upload code files and ask questions about them")

# File upload section
with st.sidebar:
    st.header("Upload Files")
    uploaded_files = st.file_uploader(
        "Upload code files",
        accept_multiple_files=True,
        type=["py", "js", "ts", "java", "c", "cpp", "h", "hpp", "cs", "go", "rb", "php", "html", "css"]
    )

    # Auto-index when files change
    current_files_hash = get_files_hash(uploaded_files)
    if current_files_hash != st.session_state.last_files_hash and uploaded_files:
        with st.spinner("Indexing files..."):
            success = index_uploaded_files(uploaded_files)
            if success:
                st.success(f"Successfully indexed {len(uploaded_files)} files")
                st.session_state.last_files_hash = current_files_hash

    # Keep the manual index button for cases where auto-indexing fails
    if st.button("Re-Index Files"):
        with st.spinner("Re-indexing files..."):
            success = index_uploaded_files(uploaded_files)
            if success:
                st.success(f"Successfully re-indexed {len(uploaded_files)} files")
                st.session_state.last_files_hash = current_files_hash

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
            response, context = st.session_state.rag.process_query(query)

            st.markdown("### Answer")
            st.markdown(response)

            # Display the context that was sent to Gemini
            with st.expander("View Context Sent to Gemini"):
                st.code(context, language="text")

# Environment setup instructions
with st.sidebar:
    st.header("Setup Instructions")
    st.markdown("""
    1. Create a `.env` file in the project root
    2. Add your Gemini API key: `GEMINI_API_KEY=your_key_here`
    3. Restart the app
    """)

    # Add button to reset everything
    st.header("Reset App")
    if st.button("Reset Everything"):
        # Clean up
        cleanup_temp_files()

        # Delete data directory
        if os.path.exists(DATA_DIR):
            try:
                shutil.rmtree(DATA_DIR)
                os.makedirs(DATA_DIR, exist_ok=True)
            except Exception as e:
                st.error(f"Error clearing data: {str(e)}")

        # Reinitialize RAG
        st.session_state.rag = CodeRAG(persist_directory=DATA_DIR)
        st.session_state.indexed_files = []
        st.session_state.last_files_hash = ""

        st.success("Reset complete. App state has been cleared.")
        st.experimental_rerun()

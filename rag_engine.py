import os
import chromadb
import google.generativeai as genai
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

class CodeRAG:
    def __init__(self, persist_directory="./data"):
        """Initialize the RAG engine with ChromaDB."""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Create or get collection
        try:
            self.collection = self.client.get_collection(name="code_snippets")
            print("Using existing collection")
        except Exception:
            print("Creating new collection")
            self.collection = self.client.create_collection(
                name="code_snippets",
                metadata={"hnsw:space": "cosine"}
            )

        # Initialize Gemini model - using the 2.0 Flash model
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def add_documents(self, code_elements: List[Dict[str, Any]]) -> None:
        """
        Add code elements to the vector database.
        """
        if not code_elements:
            return

        ids = [element["id"] for element in code_elements]
        documents = [f"{element['description']}\n{element['code']}" for element in code_elements]
        metadatas = [{
            "type": element["type"],
            "file_path": element["file_path"],
            "name": element.get("name", ""),
            "description": element["description"],
        } for element in code_elements]

        # Add to collection
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        print(f"Added {len(code_elements)} code elements to the database.")

    def clear_collection(self):
        """Clear all documents from the collection by recreating it"""
        try:
            # Delete the collection completely
            self.client.delete_collection("code_snippets")
            print("Deleted existing collection")

            # Create a new empty collection
            self.collection = self.client.create_collection(
                name="code_snippets",
                metadata={"hnsw:space": "cosine"}
            )
            print("Created new empty collection")
            return True
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant code elements based on query.
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
            )

            if not results["ids"] or len(results["ids"][0]) == 0:
                return []

            return [{
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
            } for i in range(len(results["ids"][0]))]
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return []

    def generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Generate a response using Gemini API based on query and retrieved context.
        Returns both the response and the context sent to Gemini.
        """
        if not context_docs:
            return "No relevant code found to answer your question.", "No context available."

        # Create context from retrieved documents
        context = "\n\n".join([f"File: {doc['metadata']['file_path']}\n{doc['document']}"
                             for doc in context_docs])

        # Prompt for Gemini
        prompt = f"""
        You are a helpful AI assistant specialized in answering questions about code.
        Please answer the following question based on the code context provided.

        Code context:
        {context}

        Question: {query}

        Give a detailed and helpful response, referencing specific parts of the code where relevant.
        """

        # Generate response
        response = self.model.generate_content(prompt)
        return response.text, context

    def process_query(self, query: str, n_results: int = 5) -> Tuple[str, str]:
        """
        Process a user query by retrieving relevant code and generating a response.
        Returns both the response and the context sent to Gemini.
        """
        # Search for relevant code
        search_results = self.search(query, n_results)

        # Generate response based on retrieved context
        response, context = self.generate_response(query, search_results)

        return response, context

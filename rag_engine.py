import os
import json
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv
import pickle

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

class SimpleVectorStore:
    def __init__(self, persist_directory='./data'):
        """A simple vector store implementation"""
        self.persist_directory = persist_directory
        self.embeddings = []
        self.documents = []

        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Try to load existing data
        self.load()

    def add_documents(self, documents, embeddings):
        """Add documents and their embeddings to the store"""
        self.documents.extend(documents)
        self.embeddings.extend(embeddings)
        self.persist()

    def similarity_search(self, query_embedding, k=5):
        """Find the most similar documents to the query embedding"""
        if not self.embeddings:
            return []

        # Convert list to numpy array for efficient computation
        embeddings_array = np.array(self.embeddings)
        query_embedding = np.array(query_embedding).reshape(1, -1)

        # Calculate similarities
        similarities = cosine_similarity(query_embedding, embeddings_array)[0]

        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:k]

        # Return top documents
        results = []
        for idx in top_indices:
            results.append({
                "document": self.documents[idx],
                "score": similarities[idx]
            })

        return results

    def delete_collection(self):
        """Clear all documents and embeddings"""
        self.documents = []
        self.embeddings = []
        self.persist()

    def persist(self):
        """Save the vector store to disk"""
        data = {
            "documents": self.documents,
            "embeddings": self.embeddings
        }
        with open(os.path.join(self.persist_directory, 'vector_store.pkl'), 'wb') as f:
            pickle.dump(data, f)

    def load(self):
        """Load the vector store from disk"""
        file_path = os.path.join(self.persist_directory, 'vector_store.pkl')
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get("documents", [])
                    self.embeddings = data.get("embeddings", [])
            except Exception as e:
                print(f"Error loading vector store: {e}")

class CodeRAG:
    def __init__(self, persist_directory='./data'):
        """Initialize the CodeRAG engine with embeddings model and vector store."""
        self.persist_directory = persist_directory

        # Load sentence transformer model for embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize simple vector store
        self.vectorstore = SimpleVectorStore(persist_directory)

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store."""
        formatted_docs = []
        texts_to_embed = []

        for doc in documents:
            code = doc.get("code", "")
            description = doc.get("description", "")
            doc_type = doc.get("type", "unknown")
            file_path = doc.get("file_path", "")

            # Create a document with all fields
            formatted_doc = {
                "content": code,
                "metadata": {
                    "description": description,
                    "type": doc_type,
                    "file_path": file_path,
                    **{k: v for k, v in doc.items() if k not in ["code", "description"]}
                }
            }

            formatted_docs.append(formatted_doc)
            # Combine code and description for better embeddings
            texts_to_embed.append(f"{description} {code}")

        # Generate embeddings in batches to avoid memory issues
        batch_size = 32
        all_embeddings = []

        for i in range(0, len(texts_to_embed), batch_size):
            batch_texts = texts_to_embed[i:i+batch_size]
            batch_embeddings = self.model.encode(batch_texts).tolist()
            all_embeddings.extend(batch_embeddings)

        # Add to vector store
        if formatted_docs:
            self.vectorstore.add_documents(formatted_docs, all_embeddings)

    def clear_collection(self):
        """Clear the vector store collection."""
        self.vectorstore.delete_collection()

    def process_query(self, query: str, k: int = 5) -> Tuple[str, str]:
        """
        Process a query about the code and return a response with context.

        Args:
            query: The query to process
            k: Number of most similar chunks to retrieve

        Returns:
            Tuple[str, str]: (response, context)
        """
        # Generate embedding for the query
        query_embedding = self.model.encode([query])[0].tolist()

        # Search for relevant code chunks
        results = self.vectorstore.similarity_search(query_embedding, k=k+5)

        if not results:
            return "No relevant code found to answer your question.", "No context available."

        # Prepare context with file path information
        file_chunks = {}
        for result in results:
            doc = result["document"]
            content = doc["content"]
            metadata = doc["metadata"]
            file_path = metadata.get("file_path", "Unknown")
            code_type = metadata.get("type", "unknown")
            file_name = os.path.basename(file_path)

            # Skip duplicate content from the same file
            if file_path in file_chunks and content in file_chunks[file_path]["content"]:
                continue

            if file_path not in file_chunks:
                file_chunks[file_path] = {
                    "file_name": file_name,
                    "content": [],
                    "types": set()
                }

            file_chunks[file_path]["content"].append(content)
            file_chunks[file_path]["types"].add(code_type)

        # Build context string, ensuring we include a diverse set of files
        context = ""
        included_files = set()

        # First include non-Python files to ensure they're represented
        for file_path, data in file_chunks.items():
            if file_path.lower().endswith(('.java', '.js', '.ts', '.cpp', '.c', '.cs', '.go')) and file_path not in included_files:
                if len(included_files) < k:  # Limit to k files total
                    context += f"--- File: {data['file_name']} ---\n"
                    context += "\n".join(data["content"])
                    context += "\n\n"
                    included_files.add(file_path)

        # Then include any remaining files up to k
        for file_path, data in file_chunks.items():
            if file_path not in included_files:
                if len(included_files) < k:  # Limit to k files total
                    context += f"--- File: {data['file_name']} ---\n"
                    context += "\n".join(data["content"])
                    context += "\n\n"
                    included_files.add(file_path)

        # Generate response using Gemini
        prompt = f"""
        You are a code expert assistant. Based on the following code context, please answer the user's question.
        Be specific, detailed, and reference relevant parts of the code in your answer.

        CODE CONTEXT:
        {context}

        QUESTION: {query}
        """

        try:
            response = gemini_model.generate_content(prompt)
            return response.text, context
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            return error_msg, context

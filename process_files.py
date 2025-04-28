from map import LANGUAGE_MAP
import os
import uuid
from typing import Dict, List, Any
import code_indexer
def process_non_python_file(file_path: str) -> List[Dict[str, Any]]:
    """Process non-Python files by chunking them appropriately"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # For simplicity, chunk by logical sections if possible
        # Basic chunking strategy - can be improved based on file type
        chunks = []
        lines = content.split("\n")

        # Create chunks of max ~100 lines
        chunk_size = 100
        for i in range(0, len(lines), chunk_size):
            chunk_content = "\n".join(lines[i : i + chunk_size])
            if chunk_content.strip():
                chunks.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": "code_chunk",
                        "code": chunk_content,
                        "file_path": file_path,
                        "line_range": f"{i+1}-{min(i+chunk_size, len(lines))}",
                        "description": f"Code chunk (lines {i+1}-{min(i+chunk_size, len(lines))}) from {os.path.basename(file_path)}",
                    }
                )

        return chunks

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []


def process_file(file_path: str) -> List[Dict[str, Any]]:
    """Process a single file based on its extension using tree-sitter if available."""
    _, ext = os.path.splitext(file_path)
    lang_name = LANGUAGE_MAP.get(ext.lower())

    if lang_name:
        # Try processing with tree-sitter via the language pack
        # Ensure lang_name is of type SupportedLanguage if your map is typed
        return code_indexer.extract_elements_with_tree_sitter(file_path, lang_name)
    else:
        # Fallback for unsupported or non-code files
        print(f"No specific parser mapped for extension '{ext}'. Skipping {file_path}.")
        # return process_non_python_file(file_path) # Or just return empty
        return []

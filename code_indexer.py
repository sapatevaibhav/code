import os
import ast
import astunparse
import uuid
from typing import Dict, List, Any
import sys

# Add the path to code-chunker if not already in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from lib.code_chunker.Chunker import CodeChunker
from lib.code_chunker.CodeParser import CodeParser
from code_utils import count_tokens

def get_supported_extensions() -> List[str]:
    """
    Get a list of file extensions supported by the code-chunker library.
    If the CodeParser doesn't have get_supported_extensions method,
    return a predefined list of common extensions.

    Returns:
        List[str]: List of supported file extensions with the dot prefix (e.g., ['.py', '.js'])
    """
    # Create a CodeParser instance
    parser = CodeParser([])

    # Try to get supported extensions from parser
    try:
        extensions = parser.get_supported_extensions()
    except AttributeError:
        # If method doesn't exist, use a predefined list of common extensions
        extensions = ['py', 'js', 'java', 'ts', 'html', 'css', 'go', 'rb', 'php', 'cs', 'cpp', 'c']

    # Add the dot prefix to extensions if not already present
    return [f".{ext}" if not ext.startswith('.') else ext for ext in extensions]

def extract_code_elements(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a Python file and extract meaningful code elements using AST.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        # Extract elements
        elements = []

        # Process imports
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        if imports:
            import_code = "\n".join(astunparse.unparse(imp).strip() for imp in imports)
            elements.append({
                "id": str(uuid.uuid4()),
                "type": "imports",
                "code": import_code,
                "file_path": file_path,
                "description": f"Import statements from {os.path.basename(file_path)}"
            })

        # Process classes
        for node in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            class_code = astunparse.unparse(node).strip()
            docstring = ast.get_docstring(node) or "No documentation"
            elements.append({
                "id": str(uuid.uuid4()),
                "type": "class",
                "name": node.name,
                "code": class_code,
                "file_path": file_path,
                "line_number": node.lineno,
                "docstring": docstring,
                "description": f"Class {node.name} from {os.path.basename(file_path)}"
            })

        # Process functions
        for node in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            func_code = astunparse.unparse(node).strip()
            docstring = ast.get_docstring(node) or "No documentation"
            parent = next((p.name for p in ast.walk(tree) if isinstance(p, ast.ClassDef) and
                          node.lineno > p.lineno and
                          node.lineno < (p.end_lineno if hasattr(p, 'end_lineno') else float('inf'))),
                         None)

            elements.append({
                "id": str(uuid.uuid4()),
                "type": "function",
                "name": node.name,
                "code": func_code,
                "file_path": file_path,
                "line_number": node.lineno,
                "docstring": docstring,
                "parent_class": parent,
                "description": f"{'Method' if parent else 'Function'} {node.name} from {os.path.basename(file_path)}"
            })

        return elements

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []

def process_non_python_file(file_path: str) -> List[Dict[str, Any]]:
    """Process non-Python files by chunking them appropriately"""
    try:
        _, ext = os.path.splitext(file_path)
        ext = ext.lstrip('.').lower()  # Remove the dot and convert to lowercase

        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Use the CodeChunker class as per documentation
        chunker = CodeChunker(file_extension=ext, encoding_name='gpt-4')
        chunks = chunker.chunk(content, token_limit=1000)

        results = []
        # The chunks are returned as a dict with chunk numbers as keys
        for chunk_num, chunk_content in chunks.items():
            # Count the lines for start and end line numbers
            start_line = 1
            if chunk_num > 1 and chunk_num-1 in chunks:
                start_line = content[:content.find(chunks[chunk_num])].count('\n') + 1
            end_line = start_line + chunk_content.count('\n')

            results.append({
                "id": str(uuid.uuid4()),
                "type": "code_chunk",
                "code": chunk_content,
                "file_path": file_path,
                "chunk_number": chunk_num,
                "line_range": f"{start_line}-{end_line}",
                "description": f"Code chunk {chunk_num} (lines {start_line}-{end_line}) from {os.path.basename(file_path)}"
            })

        return results

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []

def process_file(file_path: str) -> List[Dict[str, Any]]:
    """Process a single file based on its extension."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()  # Keep the dot prefix

    if ext == '.py':
        return extract_code_elements(file_path)
    else:
        # Check if the extension is supported by the CodeChunker
        supported_extensions = get_supported_extensions()
        if ext in supported_extensions:
            return process_non_python_file(file_path)
        else:
            print(f"Unsupported file extension: {ext}")
            return []

def index_files(file_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Index multiple files and return all code elements.
    """
    all_elements = []
    for file_path in file_paths:
        elements = process_file(file_path)
        all_elements.extend(elements)

    return all_elements

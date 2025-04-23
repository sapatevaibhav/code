import os
import ast
import astunparse
import uuid
from typing import Dict, List, Any

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
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # For simplicity, chunk by logical sections if possible
        # Basic chunking strategy - can be improved based on file type
        chunks = []
        lines = content.split('\n')

        # Create chunks of max ~100 lines
        chunk_size = 100
        for i in range(0, len(lines), chunk_size):
            chunk_content = '\n'.join(lines[i:i+chunk_size])
            if chunk_content.strip():
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "type": "code_chunk",
                    "code": chunk_content,
                    "file_path": file_path,
                    "line_range": f"{i+1}-{min(i+chunk_size, len(lines))}",
                    "description": f"Code chunk (lines {i+1}-{min(i+chunk_size, len(lines))}) from {os.path.basename(file_path)}"
                })

        return chunks

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []

def process_file(file_path: str) -> List[Dict[str, Any]]:
    """Process a single file based on its extension."""
    _, ext = os.path.splitext(file_path)

    if ext.lower() == '.py':
        return extract_code_elements(file_path)
    else:
        return process_non_python_file(file_path)

def index_files(file_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Index multiple files and return all code elements.
    """
    all_elements = []
    for file_path in file_paths:
        elements = process_file(file_path)
        all_elements.extend(elements)

    return all_elements

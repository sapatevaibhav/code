import os
import uuid
from typing import Dict, List, Any, Optional

# Remove direct Language, Parser import if only using the pack's functions
# from tree_sitter import Language, Parser
# Import the necessary functions from the language pack
from tree_sitter_language_pack import (
    get_language as get_ts_language,
    get_parser as get_ts_parser,
    SupportedLanguage,
)
from tree_sitter import Language, Parser, Node  # Keep Node for type hints if needed

# --- Tree-sitter Setup ---
# LANGUAGE_LIB_PATH = 'build/languages.so' # Path to the built library <-- REMOVE/COMMENT OUT
# Ensure the library exists before proceeding <-- REMOVE/COMMENT OUT
# if not os.path.exists(LANGUAGE_LIB_PATH):
#     raise RuntimeError(f"Language library not found at {LANGUAGE_LIB_PATH}. "
#                      "Please run build_parsers.py first.") <-- REMOVE/COMMENT OUT

# Map file extensions to tree-sitter language names
# Ensure these names match the 'SupportedLanguage' literal type in tree_sitter_language_pack
LANGUAGE_MAP: Dict[str, SupportedLanguage] = {
    # Core Web
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",  # JSX handled via tree-sitter-javascript
    ".ts": "typescript",
    ".tsx": "tsx",  # Requires separate grammar from tree-sitter-typescript
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".rb": "ruby",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".cs": "csharp",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".yaml": "yaml",
    ".toml": "toml",

    # Additional major languages
    ".sh": "bash",
    ".zsh": "bash",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".pl": "perl",
    ".pm": "perl",
    ".r": "r",
    ".lua": "lua",
    ".sql": "sql",
    ".hs": "haskell",
    ".erl": "erlang",
    ".ex": "elixir",
    ".ml": "ocaml",
    ".fs": "fsharp",
    ".clj": "clojure",
    ".dart": "dart",
    ".groovy": "groovy",
    ".jl": "julia",
    ".scm": "scheme",
    ".vim": "vimscript",
    ".zig": "zig",
    ".odin": "odin",

    # Configuration/markup
    ".xml": "xml",
    ".md": "markdown",
    ".rst": "rst",
    ".tex": "latex",
    ".nim": "nim",
    ".pkl": "pkl",

    # Modern web/extensions
    ".vue": "vue",
    ".svelte": "svelte",
    ".graphql": "graphql",
    ".proto": "proto",

    # Scripting
    ".ps1": "powershell",
    ".jl": "julia",
    ".tcl": "tcl",
    ".m": "matlab",

    # Shell configurations
    ".bashrc": "bash",
    ".zshrc": "bash",

    # Special cases
    ".Dockerfile": "dockerfile",
    "Dockerfile": "dockerfile",
    ".gitignore": "gitignore",
    ".gitattributes": "gitattributes",
    "Makefile": "make",

    # Experimental/less common
    ".wat": "wat",
    ".wast": "wat",
    ".ql": "ql",  # CodeQL
    ".blade.php": "blade",
    ".eex": "embedded_template",  # Elixir
    ".heex": "embedded_template",  # Elixir
}


# Cache loaded languages/parsers (optional, pack might cache internally)
LOADED_LANGUAGES: Dict[str, Language] = {}
LOADED_PARSERS: Dict[str, Parser] = {}


def get_language_and_parser(
    lang_name: SupportedLanguage,
) -> Optional[tuple[Language, Parser]]:
    """Loads a tree-sitter language and parser using tree_sitter_language_pack."""
    if lang_name not in LOADED_PARSERS:
        try:
            # Use the functions from the language pack
            language = get_ts_language(lang_name)
            parser = get_ts_parser(lang_name)
            LOADED_LANGUAGES[lang_name] = language
            LOADED_PARSERS[lang_name] = parser
        except LookupError:
            print(
                f"Warning: Language '{lang_name}' not supported by tree_sitter_language_pack."
            )
            return None
        except Exception as e:
            print(f"Warning: Could not load language '{lang_name}' using pack: {e}")
            return None
    return LOADED_LANGUAGES.get(lang_name), LOADED_PARSERS.get(lang_name)


# --- End Tree-sitter Setup ---


def extract_elements_with_tree_sitter(
    file_path: str, language_name: SupportedLanguage
) -> List[Dict[str, Any]]:
    """
    Parse a file using tree-sitter and extract meaningful code elements.
    """
    lang_parser_tuple = get_language_and_parser(language_name)
    if not lang_parser_tuple:
        print(
            f"Skipping {file_path}: Language '{language_name}' not supported or loaded via pack."
        )
        return []  # Or fallback

    language, parser = lang_parser_tuple

    # parser = Parser() # Parser is already created by get_parser
    # parser.set_language(language) # Parser is already configured by get_parser

    elements = []
    try:
        with open(file_path, "rb") as f:
            content_bytes = f.read()

        tree = parser.parse(content_bytes)
        root_node = tree.root_node

        # --- Language-Specific Queries ---
        # These queries identify top-level functions and classes.
        # You'll need to refine these and add queries for other languages.
        queries = {
            "python": """
                (function_definition name: (identifier) @function.name) @function.definition
                (class_definition name: (identifier) @class.name) @class.definition
            """,
            "java": """
                (method_declaration name: (identifier) @function.name) @function.definition
                (class_declaration name: (identifier) @class.name) @class.definition
                (interface_declaration name: (identifier) @class.name) @class.definition
            """,
            "javascript": """
                (function_declaration name: (identifier) @function.name) @function.definition
                (lexical_declaration (variable_declarator name: (identifier) @function.name value: [(arrow_function) (function)])) @function.definition
                (expression_statement (assignment_expression left: [(identifier) (member_expression)] @function.name right: [(arrow_function) (function)])) @function.definition
                (class_declaration name: (identifier) @class.name) @class.definition
             """,
            "c": """
                (function_definition declarator: (function_declarator declarator: (identifier) @function.name)) @function.definition
                (struct_specifier name: (type_identifier) @class.name) @class.definition
                (union_specifier name: (type_identifier) @class.name) @class.definition
                (enum_specifier name: (type_identifier) @class.name) @class.definition
             """,
            "cpp": """
                (function_definition declarator: [
                    (function_declarator declarator: (identifier) @function.name)
                    (function_declarator declarator: (qualified_identifier name: (identifier) @function.name))
                    (function_declarator declarator: (field_identifier) @function.name) # Methods
                 ]) @function.definition
                (class_specifier name: (type_identifier) @class.name) @class.definition
                (struct_specifier name: (type_identifier) @class.name) @class.definition
                (union_specifier name: (type_identifier) @class.name) @class.definition
                (enum_specifier name: (type_identifier) @class.name) @class.definition
             """,
            "csharp": """
                (method_declaration name: (identifier) @function.name) @function.definition
                (class_declaration name: (identifier) @class.name) @class.definition
                (struct_declaration name: (identifier) @class.name) @class.definition
                (interface_declaration name: (identifier) @class.name) @class.definition
                (enum_declaration name: (identifier) @class.name) @class.definition
             """,
            # Add queries for other languages supported by the pack
        }

        query_string = queries.get(language_name)
        if not query_string:
            print(
                f"Warning: No tree-sitter query defined for language '{language_name}'. Falling back to basic chunking."
            )
            # Optionally fall back to process_non_python_file or just return []
            # return process_non_python_file(file_path) # Fallback example
            return []

        query = language.query(query_string)
        captures_dict = query.captures(root_node)  # Rename to captures_dict

        # --- DEBUGGING: Print captures ---
        print(f"--- Captures Dict for {file_path} ({language_name}) ---")
        print(captures_dict)
        print(f"--- End Captures Dict ---")
        # --- END DEBUGGING ---

        processed_definition_nodes = set()  # Keep track of processed definitions

        # Iterate through capture types relevant for definitions (e.g., function.definition, class.definition)
        for capture_name, definition_nodes in captures_dict.items():
            if not capture_name.endswith(".definition"):
                continue  # Skip if it's not a definition capture type (like .name)

            element_type_base = capture_name.split(".")[0]  # 'function' or 'class'
            name_capture_key = f"{element_type_base}.name"  # Corresponding name key

            name_nodes = captures_dict.get(
                name_capture_key, []
            )  # Get the list of name nodes

            for definition_node in definition_nodes:
                if definition_node.id in processed_definition_nodes:
                    continue

                element_name = "Unknown"
                # Find the corresponding name node for this specific definition node
                for name_node in name_nodes:
                    # Check if the name node is within the byte range of the definition node
                    if (
                        name_node.start_byte >= definition_node.start_byte
                        and name_node.end_byte <= definition_node.end_byte
                    ):
                        element_name = name_node.text.decode("utf-8", errors="ignore")
                        break  # Found the name for this definition

                element_type = element_type_base  # Use 'function' or 'class' directly

                # Now create the element dictionary
                code_segment = definition_node.text.decode("utf-8", errors="ignore")
                start_line = definition_node.start_point[0] + 1
                end_line = definition_node.end_point[0] + 1

                elements.append(
                    {
                        "id": str(uuid.uuid4()),
                        "type": element_type,
                        "name": element_name,
                        "code": code_segment,
                        "file_path": file_path,
                        "line_range": f"{start_line}-{end_line}",
                        "description": f"{element_type.capitalize()} {element_name} from {os.path.basename(file_path)}",
                    }
                )
                processed_definition_nodes.add(
                    definition_node.id
                )  # Mark this definition as processed

        # If no specific elements found, maybe chunk the whole file?
        if not elements and content_bytes.strip():
            print(
                f"No specific elements found via query in {file_path} for {language_name}. Consider adding a whole-file chunk or refining queries."
            )
            # Optionally add a single chunk for the whole file here
            # elements.extend(process_non_python_file(file_path))

    except Exception as e:
        print(f"Error processing {file_path} with tree-sitter pack: {str(e)}")
        # Optionally fall back to basic chunking on error
        # return process_non_python_file(file_path)
        return []

    return elements


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
        return extract_elements_with_tree_sitter(file_path, lang_name)
    else:
        # Fallback for unsupported or non-code files
        print(f"No specific parser mapped for extension '{ext}'. Skipping {file_path}.")
        # return process_non_python_file(file_path) # Or just return empty
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

from tree_sitter_language_pack import SupportedLanguage
from typing import Dict

LANGUAGE_MAP: Dict[str, SupportedLanguage] = {
    # Major languages
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
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
    ".ql": "ql",
    ".blade.php": "blade",
    ".eex": "embedded_template",
    ".heex": "embedded_template",
}

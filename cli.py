#!/usr/bin/env python3
import os
import argparse
import json
from typing import List
from code_indexer import index_files

def collect_files(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Collect all files with given extensions from a directory.
    If extensions is None, collect all files.
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not extensions:
                file_paths.append(file_path)
            else:
                _, ext = os.path.splitext(file_path)
                if ext.lower() in extensions:
                    file_paths.append(file_path)
    return file_paths

def main():
    parser = argparse.ArgumentParser(description="Code indexing utility that supports multiple languages")
    parser.add_argument("directory", help="Directory to process")
    parser.add_argument("-o", "--output", help="Output JSON file", default="code_index.json")
    parser.add_argument("-e", "--extensions", help="Comma-separated list of file extensions to process (e.g., .py,.js,.ts)", default=None)

    args = parser.parse_args()

    extensions = None
    if args.extensions:
        extensions = args.extensions.split(',')

    file_paths = collect_files(args.directory, extensions)
    print(f"Found {len(file_paths)} files to process")

    elements = index_files(file_paths)
    print(f"Indexed {len(elements)} code elements")

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(elements, f, indent=2)

    print(f"Index saved to {args.output}")

if __name__ == "__main__":
    main()

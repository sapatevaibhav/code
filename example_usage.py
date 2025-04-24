#!/usr/bin/env python3
"""
Example script demonstrating how to use the enhanced code indexer
with code_chunker integration for multi-language support.
"""
import os
import json
from code_indexer import index_files, get_supported_extensions

def main():
    # Get the list of supported file extensions
    supported_extensions = get_supported_extensions()
    print(f"Supported file extensions: {', '.join(supported_extensions)}")

    # Define directory to process
    # For this example, we'll use the code_chunker library itself
    target_dir = os.path.join(os.path.dirname(__file__), 'lib/code_chunker')

    # Find all files with supported extensions
    file_paths = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file_path)
            if ext.lower() in supported_extensions:
                file_paths.append(file_path)

    print(f"Found {len(file_paths)} files to process")
    for file_path in file_paths:
        print(f" - {os.path.relpath(file_path, target_dir)}")

    # Process all files
    print("\nProcessing files...")
    elements = index_files(file_paths)

    # Print summary of extracted elements
    element_types = {}
    for element in elements:
        element_type = element.get("type", "unknown")
        element_types[element_type] = element_types.get(element_type, 0) + 1

    print("\nExtracted elements:")
    for element_type, count in element_types.items():
        print(f" - {element_type}: {count}")

    # Save to file
    output_file = "code_index_example.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(elements, f, indent=2)

    print(f"\nSaved {len(elements)} code elements to {output_file}")

if __name__ == "__main__":
    main()

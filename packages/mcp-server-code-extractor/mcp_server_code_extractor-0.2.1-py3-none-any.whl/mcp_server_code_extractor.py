#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]",
#     "tree-sitter-languages",
#     "tree-sitter==0.21.3",
# ]
# ///
"""
MCP Extract - Simple code extraction using tree-sitter-languages

A single-file MCP server that extracts functions and classes from code files.
No more grep/sed/awk gymnastics - just clean, precise extraction.

🚨 **CRITICAL WORKFLOW GUIDANCE FOR CLAUDE** 🚨

**STOP USING READ/SEARCH/GREP FOR CODE INVESTIGATION!**

❌ **WRONG**: Read(file) → Search(pattern) → Edit
✅ **CORRECT**: get_symbols(file) → get_function(file, name) → Edit

**MANDATORY STEPS**:
1. ALWAYS start with get_symbols(file) to see what's in the file
2. Use get_function(file, name) to extract specific functions
3. Use get_class(file, name) for class definitions
4. NEVER use Read() to "examine" or "investigate" code files

**🚫 Using Read() on code files wastes context and misses structure**

**COMMON SCENARIOS**:
- Testing: get_symbols(test_file) → get_function(test_file, "test_method_name")
- Debugging: get_symbols(file) → get_function(file, "problematic_function")
- Refactoring: get_symbols(file) → get_class(file, "ClassName")
- Investigation: get_symbols(file) → get_lines(file, start, end)

Usage with uv:
  1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
  2. Run directly: uv run mcp-extract.py
  3. Configure in Claude Desktop with: uv run /path/to/mcp-extract.py

Or traditional install:
  pip install mcp[cli] tree-sitter-languages
"""

import os
import sys
from pathlib import Path

# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from code_extractor import CodeExtractor, create_extractor
    from code_extractor.models import SymbolKind
except ImportError as e:
    print(f"Error: Code extractor library not found: {e}")
    print("Make sure it's installed or run from the correct directory.")
    exit(1)

try:
    from tree_sitter_languages import get_language, get_parser
except ImportError:
    print("Error: tree-sitter-languages not installed")
    print("Run with: uv run mcp-extract.py")
    print("Or install: pip install tree-sitter-languages")
    exit(1)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: mcp not installed")
    print("Run with: uv run mcp-extract.py")
    print("Or install: pip install mcp[cli]")
    exit(1)

# Create the server
mcp = FastMCP("extract")

# Map file extensions to language names
LANG_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.cs': 'c_sharp',
    '.java': 'java',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.r': 'r',
    '.lua': 'lua',
    '.dart': 'dart',
    '.jl': 'julia',
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'bash',
    '.fish': 'fish',
    '.ps1': 'powershell',
    '.sql': 'sql',
    '.vim': 'vim',
    '.ml': 'ocaml',
    '.mli': 'ocaml',
    '.ex': 'elixir',
    '.exs': 'elixir',
    '.elm': 'elm',
    '.clj': 'clojure',
    '.cljs': 'clojure',
    '.hs': 'haskell',
    '.pl': 'perl',
    '.pm': 'perl',
    '.m': 'objc',
    '.mm': 'objc',
    '.proto': 'protobuf',
    '.vue': 'vue',
    '.svelte': 'svelte',
}


def get_language_for_file(file_path: str) -> str:
    """Get the language name for a file."""
    ext = Path(file_path).suffix.lower()
    return LANG_MAP.get(ext, 'text')


@mcp.tool()
def get_function(file_path: str, function_name: str) -> dict:
    """
    Extract a complete function definition - USE THIS INSTEAD OF Read() for specific functions!
    
    🎯 **PRECISE EXTRACTION** - Gets exact function boundaries with line numbers using tree-sitter.
    ⚠️ **REPLACES Read() + manual parsing** - No need to read entire files and search manually.
    
    Args:
        file_path: Path to the source file
        function_name: Exact name of the function to extract
        
    Returns:
        dict with code, start_line, end_line, lines, function, file, language
        
    **WORKFLOW**: get_symbols() first → get_function() for specific extraction → Edit
    """

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    lang_name = get_language_for_file(file_path)
    if lang_name == 'text':
        return {"error": f"Unsupported file type: {Path(file_path).suffix}"}

    try:
        parser = get_parser(lang_name)

        with open(file_path, 'rb') as f:
            source = f.read()

        tree = parser.parse(source)

        # Language-specific function node types
        func_types = {
            'python': ['function_definition', 'async_function_definition'],
            'javascript': ['function_declaration', 'function_expression', 'arrow_function'],
            'typescript': ['function_declaration', 'function_expression', 'arrow_function', 'method_definition'],
            'tsx': ['function_declaration', 'function_expression', 'arrow_function', 'method_definition'],
            'go': ['function_declaration', 'method_declaration'],
            'rust': ['function_item'],
            'ruby': ['method', 'singleton_method'],
            'java': ['method_declaration', 'constructor_declaration'],
            'c': ['function_definition'],
            'cpp': ['function_definition'],
            'c_sharp': ['method_declaration', 'constructor_declaration'],
            'php': ['function_definition', 'method_declaration'],
            'swift': ['function_declaration'],
            'kotlin': ['function_declaration'],
            'scala': ['function_definition'],
        }

        types = func_types.get(
            lang_name, ['function_definition', 'function_declaration'])

        # Find the function
        def find_function(node):
            if node.type in types:
                # Look for name - try multiple approaches
                name = None

                # Direct identifier child
                for child in node.children:
                    if child.type == 'identifier':
                        name = source[child.start_byte:child.end_byte].decode(
                            'utf-8')
                        if name == function_name:
                            return node
                    # For methods/properties
                    elif child.type in ['property_identifier', 'field_identifier']:
                        name = source[child.start_byte:child.end_byte].decode(
                            'utf-8')
                        if name == function_name:
                            return node

                # For some languages, name might be nested
                if hasattr(node, 'child_by_field_name'):
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = source[name_node.start_byte:name_node.end_byte].decode(
                            'utf-8')
                        if name == function_name:
                            return node

            # Recurse through children
            for child in node.children:
                result = find_function(child)
                if result:
                    return result
            return None

        func_node = find_function(tree.root_node)

        if not func_node:
            return {"error": f"Function '{function_name}' not found"}

        # Extract the function
        code = source[func_node.start_byte:func_node.end_byte].decode('utf-8')
        start_line = source[:func_node.start_byte].count(b'\n') + 1
        end_line = source[:func_node.end_byte].count(b'\n') + 1

        return {
            "code": code,
            "start_line": start_line,
            "end_line": end_line,
            "lines": f"{start_line}-{end_line}",
            "function": function_name,
            "file": file_path,
            "language": lang_name
        }

    except Exception as e:
        import traceback
        return {"error": f"Failed to parse '{file_path}': {e.__class__.__name__}: {e}", "traceback": traceback.format_exc()}


@mcp.tool()
def get_class(file_path: str, class_name: str) -> dict:
    """
    Extract a complete class definition - USE THIS INSTEAD OF Read() for specific classes!
    
    🎯 **PRECISE EXTRACTION** - Gets exact class boundaries with all methods using tree-sitter.
    ⚠️ **REPLACES Read() + manual parsing** - No need to read entire files and search manually.
    
    Args:
        file_path: Path to the source file
        class_name: Exact name of the class to extract
        
    Returns:
        dict with code, start_line, end_line, lines, class, file, language
        
    **WORKFLOW**: get_symbols() first → get_class() for specific extraction → Edit
    """

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    lang_name = get_language_for_file(file_path)
    if lang_name == 'text':
        return {"error": f"Unsupported file type: {Path(file_path).suffix}"}

    try:
        parser = get_parser(lang_name)

        with open(file_path, 'rb') as f:
            source = f.read()

        tree = parser.parse(source)

        # Language-specific class node types
        class_types = {
            'python': ['class_definition'],
            'javascript': ['class_declaration'],
            'typescript': ['class_declaration'],
            'tsx': ['class_declaration'],
            'java': ['class_declaration'],
            'c_sharp': ['class_declaration'],
            'cpp': ['class_specifier'],
            'ruby': ['class'],
            'php': ['class_declaration'],
            'swift': ['class_declaration'],
            'kotlin': ['class_declaration'],
            'scala': ['class_definition'],
            'go': ['type_declaration'],  # Go uses type for structs
            'rust': ['struct_item', 'enum_item'],
        }

        types = class_types.get(
            lang_name, ['class_declaration', 'class_definition'])

        # Find the class
        def find_class(node):
            if node.type in types:
                # Look for name
                for child in node.children:
                    if child.type in ['identifier', 'type_identifier']:
                        name = source[child.start_byte:child.end_byte].decode(
                            'utf-8')
                        if name == class_name:
                            return node

                # Try field-based access
                if hasattr(node, 'child_by_field_name'):
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = source[name_node.start_byte:name_node.end_byte].decode(
                            'utf-8')
                        if name == class_name:
                            return node

            # Recurse
            for child in node.children:
                result = find_class(child)
                if result:
                    return result
            return None

        class_node = find_class(tree.root_node)

        if not class_node:
            return {"error": f"Class '{class_name}' not found"}

        # Extract the class
        code = source[class_node.start_byte:class_node.end_byte].decode(
            'utf-8')
        start_line = source[:class_node.start_byte].count(b'\n') + 1
        end_line = source[:class_node.end_byte].count(b'\n') + 1

        return {
            "code": code,
            "start_line": start_line,
            "end_line": end_line,
            "lines": f"{start_line}-{end_line}",
            "class": class_name,
            "file": file_path,
            "language": lang_name
        }

    except Exception as e:
        import traceback
        return {"error": f"Failed to parse '{file_path}': {e.__class__.__name__}: {e}", "traceback": traceback.format_exc()}


@mcp.tool()
def get_symbols(file_path: str) -> list:
    """
    🚨 **ALWAYS USE THIS FIRST** for code investigation - DO NOT use Read() on code files!
    
    List all functions, classes, and other symbols in a file with their line numbers.
    This is the CORRECT way to explore code structure instead of reading entire files.
    
    ⚠️ **REPLACES Read() for code files** - More efficient and structured than reading entire files.
    
    Args:
        file_path: Path to the source file to analyze
        
    Returns:
        List of symbols with name, type, start_line, end_line, lines, and preview
        
    **WORKFLOW**: get_symbols() → get_function()/get_class() → Edit (NOT Read → Search → Edit)
    """

    if not os.path.exists(file_path):
        return [{"error": f"File not found: {file_path}"}]

    try:
        extractor = create_extractor(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        symbols = extractor.extract_symbols(source_code)
        
        # Convert to dict format for MCP compatibility
        result = []
        for symbol in symbols:
            result.append(symbol.to_dict())
        
        return result
        
    except Exception as e:
        return [{"error": f"Failed to parse '{file_path}': {str(e)}"}]


@mcp.tool()
def get_lines(file_path: str, start_line: int, end_line: int) -> dict:
    """
    Get specific lines from a file using precise line range control.
    
    Use this when you know exact line numbers you need (e.g., from get_symbols output) and 
    want to extract specific code sections without reading the entire file.
    
    Args:
        file_path: Path to the source file
        start_line: Starting line number (1-based, inclusive)
        end_line: Ending line number (1-based, inclusive)
        
    Returns:
        dict with code, start_line, end_line, lines, file, total_lines
        
    **WORKFLOW**: get_symbols() first → get_lines() for specific ranges → Edit
    """

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    try:
        if end_line < start_line or start_line < 1:
            return {"error": "Invalid line range - start_line must be >= 1 and <= end_line"}

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Convert to 0-based indexing
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)  # end_line is inclusive

        extracted = lines[start_idx:end_idx]

        return {
            "code": ''.join(extracted),
            "start_line": start_idx + 1,
            "end_line": start_idx + len(extracted),
            "lines": f"{start_idx + 1}-{start_idx + len(extracted)}",
            "file": file_path,
            "total_lines": len(extracted)
        }

    except Exception as e:
        import traceback
        return {"error": f"Failed to read file '{file_path}': {e.__class__.__name__}: {e}", "traceback": traceback.format_exc()}


@mcp.tool()
def get_signature(file_path: str, function_name: str) -> dict:
    """
    Get just the signature/declaration of a function without the full implementation.
    
    Use this when you only need to see function interfaces, parameters, and return types 
    for API exploration or documentation. Lighter weight than get_function.
    
    Args:
        file_path: Path to the source file
        function_name: Exact name of the function
        
    Returns:
        dict with signature, name, file, start_line, lines
        
    **WORKFLOW**: get_symbols() first → get_signature() for interface info → Edit
    """

    result = get_function(file_path, function_name)
    if "error" in result:
        return result

    # Extract just the first line (signature)
    lines = result["code"].split('\n')
    signature = lines[0]

    # For some languages, signature might span multiple lines
    # Simple heuristic: include lines until we see an opening brace or colon
    for i in range(1, min(len(lines), 5)):  # Check up to 5 lines
        signature += '\n' + lines[i]
        if '{' in lines[i] or ':' in lines[i]:
            break

    return {
        "signature": signature.strip(),
        "name": function_name,
        "file": file_path,
        "start_line": int(result["start_line"]),
        "lines": result["lines"]
    }


def main():
    """Main entry point for the MCP server."""
    import sys

    # If run with --help, show usage
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("""
mcp-server-code-extractor - A Model Context Protocol (MCP) server that provides precise code extraction tools using tree-sitter parsing

This is an MCP server that provides code extraction tools for Claude Code.

Setup for Claude Code:
  claude mcp add mcp-server-code-extractor -s user -- uv run /path/to/this/script.py

Tools provided:
  - get_function(file, name): Extract a complete function with line numbers
  - get_class(file, name): Extract a complete class with line numbers  
  - get_symbols(file): List all functions/classes with line ranges
  - get_lines(file, start, end): Get specific lines
  - get_signature(file, name): Get function signature with line number

All tools return line number information (start_line, end_line, lines).

Supported languages:
  Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, Ruby, PHP, 
  Swift, Kotlin, and 30+ more via tree-sitter-languages.

For more info: https://github.com/ctoth/mcp_server_code_extractor
        """)
        sys.exit(0)

    # Otherwise run as MCP server
    mcp.run()


if __name__ == "__main__":
    main()

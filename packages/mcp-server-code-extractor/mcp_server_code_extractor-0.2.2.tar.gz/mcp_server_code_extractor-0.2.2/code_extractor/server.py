#!/usr/bin/env python3
"""
MCP Code Extractor Server

A Model Context Protocol server that provides precise code extraction using tree-sitter.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: MCP not installed. Install with: pip install mcp[cli]", file=sys.stderr)
    sys.exit(1)

try:
    from tree_sitter_languages import get_parser
except ImportError:
    print("Error: tree-sitter-languages not installed. Install with: pip install tree-sitter-languages", file=sys.stderr)
    sys.exit(1)

# Local imports
from .extractor import create_extractor
from .languages import get_language_for_file


# Language mapping for file extensions
LANG_MAP = {
    # Python
    '.py': 'python',
    '.pyi': 'python',
    '.pyx': 'python',
    '.pxd': 'python',
    '.pxd.in': 'python',
    '.pxi': 'python',
    
    # JavaScript/TypeScript
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.mjs': 'javascript',
    '.cjs': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.d.ts': 'typescript',
    
    # Web
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'css',
    
    # Systems languages
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.cxx': 'cpp',
    '.cc': 'cpp',
    '.hpp': 'cpp',
    '.hxx': 'cpp',
    '.C': 'cpp',
    '.H': 'cpp',
    '.rs': 'rust',
    '.go': 'go',
    '.zig': 'zig',
    
    # JVM languages
    '.java': 'java',
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    '.scala': 'scala',
    '.sc': 'scala',
    '.clj': 'clojure',
    '.cljs': 'clojure',
    '.cljc': 'clojure',
    
    # Functional languages
    '.hs': 'haskell',
    '.lhs': 'haskell',
    '.ml': 'ocaml',
    '.mli': 'ocaml',
    '.ex': 'elixir',
    '.exs': 'elixir',
    
    # Other languages
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.m': 'objc',
    '.mm': 'objc',
    '.cs': 'c_sharp',
    '.fs': 'f_sharp',
    '.fsx': 'f_sharp',
    '.lua': 'lua',
    '.r': 'r',
    '.R': 'r',
    '.jl': 'julia',
    '.dart': 'dart',
    
    # Shell and config
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'bash',
    '.fish': 'bash',
    '.ps1': 'powershell',
    '.psm1': 'powershell',
    '.psd1': 'powershell',
    
    # Data and config
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.xml': 'xml',
    '.sql': 'sql',
    '.proto': 'proto',
    
    # Documentation
    '.md': 'markdown',
    '.markdown': 'markdown',
    '.rst': 'rst',
    '.tex': 'latex',
}


def get_language_for_file(file_path: str) -> str:
    """Get the language name for a file."""
    ext = Path(file_path).suffix.lower()
    return LANG_MAP.get(ext, 'text')


def find_function(node) -> dict:
    """
    Extract function definition - USE THIS INSTEAD OF Read() for specific functions!
    
    DON'T use Read() + grep/search. Use this for precise extraction with tree-sitter.
    
    If you're looking for a specific function, this is better than searching.
    """
    
    def get_function(file_path: str, function_name: str) -> dict:
        """Extract a specific function from a file."""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        try:
            lang_name = get_language_for_file(file_path)
            
            # Get tree-sitter parser
            try:
                parser = get_parser(lang_name)
            except Exception:
                return {"error": f"Language '{lang_name}' not supported"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = parser.parse(source)
            
            # Define function node types for different languages
            func_types = {
                'python': ['function_definition', 'async_function_definition'],
                'javascript': ['function_declaration', 'function_expression', 
                              'arrow_function', 'method_definition'],
                'typescript': ['function_declaration', 'function_expression', 
                              'arrow_function', 'method_definition', 'method_signature'],
                'java': ['method_declaration', 'constructor_declaration'],
                'cpp': ['function_definition', 'function_declarator'],
                'c': ['function_definition', 'function_declarator'],
                'go': ['function_declaration', 'method_declaration'],
                'rust': ['function_item'],
                'ruby': ['method', 'singleton_method'],
                'php': ['function_definition', 'method_declaration'],
            }
            
            types = func_types.get(
                lang_name, ['function_definition', 'function_declaration'])
            
            def find_function(node):
                if node.type in types:
                    # Extract function name
                    name = None
                    for child in node.children:
                        if child.type == 'identifier':
                            name = source[child.start_byte:child.end_byte].decode(
                                'utf-8') if isinstance(source, bytes) else source[child.start_byte:child.end_byte]
                            break
                        elif hasattr(child, 'children'):
                            for grandchild in child.children:
                                if grandchild.type == 'identifier':
                                    name = source[grandchild.start_byte:grandchild.end_byte].decode(
                                        'utf-8') if isinstance(source, bytes) else source[grandchild.start_byte:grandchild.end_byte]
                                    break
                            if name:
                                break
                    
                    # Use field name if available (more reliable)
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = source[name_node.start_byte:name_node.end_byte].decode(
                            'utf-8') if isinstance(source, bytes) else source[name_node.start_byte:name_node.end_byte]
                    
                    if name == function_name:
                        return node
                
                for child in node.children:
                    result = find_function(child)
                    if result:
                        return result
                return None
            
            func_node = find_function(tree.root_node)
            
            if not func_node:
                return {"error": f"Function '{function_name}' not found in {file_path}"}
            
            # Extract the function code
            source_bytes = source.encode('utf-8') if isinstance(source, str) else source
            code = source[func_node.start_byte:func_node.end_byte]
            start_line = source[:func_node.start_byte].count('\n') + 1 if isinstance(source, str) else source_bytes[:func_node.start_byte].count(b'\n') + 1
            end_line = source[:func_node.end_byte].count('\n') + 1 if isinstance(source, str) else source_bytes[:func_node.end_byte].count(b'\n') + 1
            
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
            return {"error": f"Failed to parse '{file_path}': {str(e)}"}
    
    return get_function


def find_class(node) -> dict:
    """
    Extract class definition - USE THIS INSTEAD OF Read() for specific classes!
    
    DON'T use Read() + grep/search. Use this for precise extraction with tree-sitter.
    
    If you're looking for a specific class, this is better than searching.
    """
    
    def get_class(file_path: str, class_name: str) -> dict:
        """Extract a specific class from a file."""
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        try:
            lang_name = get_language_for_file(file_path)
            
            # Get tree-sitter parser
            try:
                parser = get_parser(lang_name)
            except Exception:
                return {"error": f"Language '{lang_name}' not supported"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = parser.parse(source)
            
            # Define class node types for different languages
            class_types = {
                'python': ['class_definition'],
                'javascript': ['class_declaration'],
                'typescript': ['class_declaration'],
                'java': ['class_declaration'],
                'cpp': ['class_specifier'],
                'c': ['struct_specifier'],
                'go': ['type_declaration'],
                'rust': ['struct_item', 'enum_item', 'impl_item'],
                'ruby': ['class'],
                'php': ['class_declaration'],
                'swift': ['class_declaration'],
                'kotlin': ['class_declaration'],
                'scala': ['class_definition'],
                'csharp': ['class_declaration'],
            }
            
            types = class_types.get(
                lang_name, ['class_declaration', 'class_definition'])
            
            def find_class(node):
                if node.type in types:
                    # Extract class name
                    for child in node.children:
                        if child.type == 'identifier':
                            name = source[child.start_byte:child.end_byte].decode(
                                'utf-8') if isinstance(source, bytes) else source[child.start_byte:child.end_byte]
                            if name == class_name:
                                return node
                    
                    # Use field name if available (more reliable)
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = source[name_node.start_byte:name_node.end_byte].decode(
                            'utf-8') if isinstance(source, bytes) else source[name_node.start_byte:name_node.end_byte]
                        if name == class_name:
                            return node
                
                for child in node.children:
                    result = find_class(child)
                    if result:
                        return result
                return None
            
            class_node = find_class(tree.root_node)
            
            if not class_node:
                return {"error": f"Class '{class_name}' not found in {file_path}"}
            
            # Extract the class code
            source_bytes = source.encode('utf-8') if isinstance(source, str) else source
            code = source[class_node.start_byte:class_node.end_byte]
            start_line = source[:class_node.start_byte].count('\n') + 1 if isinstance(source, str) else source_bytes[:class_node.start_byte].count(b'\n') + 1
            end_line = source[:class_node.end_byte].count('\n') + 1 if isinstance(source, str) else source_bytes[:class_node.end_byte].count(b'\n') + 1
            
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
            return {"error": f"Failed to parse '{file_path}': {str(e)}"}
    
    return get_class


def get_symbols(file_path: str) -> list:
    """
    🚨 **ALWAYS USE THIS FIRST** for code investigation - DO NOT use Read()!
    
    List all functions, classes, and symbols with line numbers.
    
    DON'T read entire files to understand code structure - use this instead.
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


def get_lines(file_path: str, start_line: int, end_line: int) -> dict:
    """
    Get specific lines from a file using precise line range control.
    
    Use when you know exact line numbers - better than reading entire files.
    """
    
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    try:
        if start_line < 1:
            return {"error": "start_line must be >= 1"}
        
        if end_line < start_line:
            return {"error": "end_line must be >= start_line"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Convert to 0-based indexing
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        extracted = lines[start_idx:end_idx]
        
        return {
            "code": "".join(extracted),
            "start_line": start_line,
            "end_line": min(end_line, len(lines)),
            "lines": f"{start_line}-{min(end_line, len(lines))}",
            "file": file_path
        }
        
    except Exception as e:
        return {"error": f"Failed to read '{file_path}': {str(e)}"}


def get_signature(file_path: str, function_name: str) -> dict:
    """
    Get just the signature/declaration of a function without full implementation.
    
    Use for function interfaces, parameters, return types. Lighter than get_function.
    """
    
    result = find_function(None)(file_path, function_name)
    
    if "error" in result:
        return result
    
    # Extract just the first line (signature)
    lines = result["code"].split('\n')
    signature = lines[0]
    
    return {
        "signature": signature,
        "function": function_name,
        "file": file_path,
        "start_line": result["start_line"]
    }


def main():
    """Main entry point for the MCP server."""
    # Initialize FastMCP server
    mcp = FastMCP("extract")
    
    @mcp.tool()
    def get_symbols_tool(file_path: str) -> list:
        """
        🚨 **ALWAYS USE THIS FIRST** for code investigation - DO NOT use Read()!
        
        List all functions, classes, and symbols with line numbers.
        
        DON'T read entire files to understand code structure - use this instead.
        """
        return get_symbols(file_path)
    
    @mcp.tool()
    def get_function_tool(file_path: str, function_name: str) -> dict:
        """
        Extract function definition - USE THIS INSTEAD OF Read() for specific functions!
        
        DON'T use Read() + grep/search. Use this for precise extraction with tree-sitter.
        
        If you're looking for a specific function, this is better than searching.
        """
        return find_function(None)(file_path, function_name)
    
    @mcp.tool()
    def get_class_tool(file_path: str, class_name: str) -> dict:
        """
        Extract class definition - USE THIS INSTEAD OF Read() for specific classes!
        
        DON'T use Read() + grep/search. Use this for precise extraction with tree-sitter.
        
        If you're looking for a specific class, this is better than searching.
        """
        return find_class(None)(file_path, class_name)
    
    @mcp.tool()
    def get_lines_tool(file_path: str, start_line: int, end_line: int) -> dict:
        """
        Get specific lines from a file using precise line range control.
        
        Use when you know exact line numbers - better than reading entire files.
        """
        return get_lines(file_path, start_line, end_line)
    
    @mcp.tool()
    def get_signature_tool(file_path: str, function_name: str) -> dict:
        """
        Get just the signature/declaration of a function without full implementation.
        
        Use for function interfaces, parameters, return types. Lighter than get_function.
        """
        return get_signature(file_path, function_name)
    
    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
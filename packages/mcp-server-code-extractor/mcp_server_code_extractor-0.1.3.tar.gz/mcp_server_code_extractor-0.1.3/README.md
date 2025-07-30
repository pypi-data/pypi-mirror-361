# MCP Code Extractor

A Model Context Protocol (MCP) server that provides precise code extraction tools using tree-sitter parsing. Extract functions, classes, and code snippets from 30+ programming languages without manual parsing.

## Why MCP Code Extractor?

When working with AI coding assistants like Claude, you often need to:
- Extract specific functions or classes from large codebases
- Get an overview of what's in a file without reading the entire thing
- Retrieve precise code snippets with accurate line numbers
- Avoid manual parsing and grep/sed/awk gymnastics

MCP Code Extractor solves these problems by providing structured, tree-sitter-powered code extraction tools directly within your AI assistant.

## Features

- **🎯 Precise Extraction**: Uses tree-sitter parsing for accurate code boundary detection
- **🌍 30+ Languages**: Supports Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, and many more
- **📍 Line Numbers**: Every extraction includes precise line number information
- **🔍 Code Discovery**: List all functions and classes in a file before extracting
- **⚡ Fast & Lightweight**: Single-file implementation with minimal dependencies
- **🤖 AI-Optimized**: Designed specifically for use with AI coding assistants

## Installation

### Quick Start with UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone this repository
git clone https://github.com/ctoth/mcp-code-extractor
cd mcp-code-extractor

# Run directly with UV (no installation needed!)
uv run mcp_code_extractor.py
```

### Traditional Installation

```bash
pip install mcp[cli] tree-sitter-languages tree-sitter==0.21.3
```

### Configure with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "code-extractor": {
      "command": "uv",
      "args": ["run", "/path/to/mcp_code_extractor.py"]
    }
  }
}
```

Or with traditional Python:

```json
{
  "mcpServers": {
    "code-extractor": {
      "command": "python",
      "args": ["/path/to/mcp_code_extractor.py"]
    }
  }
}
```

## Available Tools

### 1. `get_symbols` - Discover Code Structure
List all functions, classes, and other symbols in a file.

```
Returns:
- name: Symbol name
- type: function/class/method/etc
- start_line/end_line: Line numbers
- preview: First line of the symbol
```

### 2. `get_function` - Extract Complete Functions
Extract a complete function with all its code.

```
Parameters:
- file_path: Path to the source file
- function_name: Name of the function to extract

Returns:
- code: Complete function code
- start_line/end_line: Precise boundaries
- language: Detected language
```

### 3. `get_class` - Extract Complete Classes
Extract an entire class definition including all methods.

```
Parameters:
- file_path: Path to the source file
- class_name: Name of the class to extract

Returns:
- code: Complete class code
- start_line/end_line: Precise boundaries
- language: Detected language
```

### 4. `get_lines` - Extract Specific Line Ranges
Get exact line ranges when you know the line numbers.

```
Parameters:
- file_path: Path to the source file
- start_line: Starting line (1-based)
- end_line: Ending line (inclusive)

Returns:
- code: Extracted lines
- line numbers and metadata
```

### 5. `get_signature` - Get Function Signatures
Quickly get just the function signature without the body.

```
Parameters:
- file_path: Path to the source file
- function_name: Name of the function

Returns:
- signature: Function signature only
- start_line: Where the function starts
```

## Usage Examples

### Example 1: Exploring a Python File

```python
# First, see what's in the file
symbols = get_symbols("src/main.py")
# Returns: List of all functions and classes with line numbers

# Extract a specific function
result = get_function("src/main.py", "process_data")
# Returns: Complete function code with line numbers

# Get just a function signature
sig = get_signature("src/main.py", "process_data")
# Returns: "def process_data(input_file: str, output_dir: Path) -> Dict[str, Any]:"
```

### Example 2: Working with Classes

```python
# Extract an entire class
result = get_class("models/user.py", "User")
# Returns: Complete User class with all methods

# Get specific lines (e.g., just the __init__ method)
lines = get_lines("models/user.py", 10, 25)
# Returns: Lines 10-25 of the file
```

### Example 3: Multi-Language Support

```javascript
// Works with JavaScript/TypeScript
symbols = get_symbols("app.ts")
func = get_function("app.ts", "handleRequest")
```

```go
// Works with Go
symbols = get_symbols("main.go")
method = get_function("main.go", "ServeHTTP")
```

## Supported Languages

- Python, JavaScript, TypeScript, JSX/TSX
- Go, Rust, C, C++, C#, Java
- Ruby, PHP, Swift, Kotlin, Scala
- Bash, PowerShell, SQL
- Haskell, OCaml, Elixir, Clojure
- And many more...

## Best Practices

1. **Always use `get_symbols` first** when exploring a new file
2. **Use `get_function/get_class`** instead of reading entire files
3. **Use `get_lines`** when you know exact line numbers
4. **Use `get_signature`** for quick API exploration

## Why Not Just Use Read?

Traditional file reading tools require you to:
- Read entire files (inefficient for large files)
- Manually parse code to find functions/classes
- Count lines manually for extraction
- Deal with complex syntax and edge cases

MCP Code Extractor:
- ✅ Extracts exactly what you need
- ✅ Provides structured data with metadata
- ✅ Handles complex syntax automatically
- ✅ Works across 30+ languages consistently

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built on [tree-sitter](https://tree-sitter.github.io/) for robust parsing
- Uses [tree-sitter-languages](https://github.com/grantjenks/py-tree-sitter-languages) for language support
- Implements the [Model Context Protocol](https://modelcontextprotocol.io/) specification

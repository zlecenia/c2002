#!/usr/bin/env python3
"""
Script to split Python file into separate files based on function definitions.
Each function will be saved as a separate file in the 'functions' directory.

Usage:
    python split_functions.py [input_file]
    
Default input file: main.py
"""

import ast
import os
import sys
import argparse
from pathlib import Path


class FunctionExtractor(ast.NodeVisitor):
    """Extract function definitions from Python AST."""
    
    def __init__(self, source_code):
        self.source_lines = source_code.splitlines()
        self.functions = []
        self.imports = []
        self.module_level_code = []
        self.current_line = 0
        
    def visit_Import(self, node):
        """Collect import statements."""
        import_lines = self._get_node_lines(node)
        self.imports.extend(import_lines)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        """Collect from-import statements."""
        import_lines = self._get_node_lines(node)
        self.imports.extend(import_lines)
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        """Extract function definitions."""
        func_lines = self._get_node_lines(node)
        
        function_info = {
            'name': node.name,
            'lines': func_lines,
            'start_line': node.lineno,
            'end_line': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + len(func_lines),
            'decorators': [self._get_decorator_text(dec) for dec in node.decorator_list],
            'docstring': ast.get_docstring(node),
            'args': [arg.arg for arg in node.args.args],
            'is_async': False
        }
        
        self.functions.append(function_info)
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        """Extract async function definitions."""
        func_lines = self._get_node_lines(node)
        
        function_info = {
            'name': node.name,
            'lines': func_lines,
            'start_line': node.lineno,
            'end_line': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + len(func_lines),
            'decorators': [self._get_decorator_text(dec) for dec in node.decorator_list],
            'docstring': ast.get_docstring(node),
            'args': [arg.arg for arg in node.args.args],
            'is_async': True
        }
        
        self.functions.append(function_info)
        self.generic_visit(node)
        
    def _get_node_lines(self, node):
        """Get source code lines for a given AST node."""
        start_line = node.lineno - 1  # Convert to 0-based indexing
        
        if hasattr(node, 'end_lineno') and node.end_lineno:
            end_line = node.end_lineno
        else:
            # Fallback: try to estimate end line
            end_line = start_line + 1
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # For functions, find the next def/class or end of file
                for i in range(start_line + 1, len(self.source_lines)):
                    line = self.source_lines[i].strip()
                    if line and not line.startswith('#') and not line.startswith(' ') and not line.startswith('\t'):
                        if line.startswith(('def ', 'class ', 'async def ')):
                            end_line = i
                            break
                else:
                    end_line = len(self.source_lines)
        
        return self.source_lines[start_line:end_line]
        
    def _get_decorator_text(self, decorator):
        """Get text representation of decorator."""
        if isinstance(decorator, ast.Name):
            return f"@{decorator.id}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return f"@{decorator.func.id}(...)"
        return "@decorator"


def create_function_file(func_info, imports, output_dir, original_filename):
    """Create a separate file for each function."""
    filename = f"{func_info['name']}.py"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        # Write header comment
        f.write(f'"""\n')
        f.write(f'Function: {func_info["name"]}\n')
        f.write(f'Extracted from: {original_filename}\n')
        f.write(f'Original line: {func_info["start_line"]}\n')
        if func_info['args']:
            f.write(f'Arguments: {", ".join(func_info["args"])}\n')
        if func_info['is_async']:
            f.write('Type: Async function\n')
        f.write('"""\n\n')
        
        # Write imports
        if imports:
            for import_line in imports:
                f.write(import_line + '\n')
            f.write('\n')
        
        # Write function code
        for line in func_info['lines']:
            f.write(line + '\n')
        
        # Add main block for testing
        f.write(f'\n\nif __name__ == "__main__":\n')
        f.write(f'    # Test the {func_info["name"]} function here\n')
        if func_info['args']:
            sample_args = ', '.join(['None' for _ in func_info['args']])
            if func_info['is_async']:
                f.write(f'    import asyncio\n')
                f.write(f'    # asyncio.run({func_info["name"]}({sample_args}))\n')
            else:
                f.write(f'    # result = {func_info["name"]}({sample_args})\n')
                f.write(f'    # print(result)\n')
        f.write(f'    pass\n')


def split_python_file(input_file, output_dir):
    """Split Python file into separate function files."""
    print(f"📁 Reading file: {input_file}")
    
    # Read source code
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found!")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Parse AST
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"❌ Syntax error in {input_file}: {e}")
        return False
    
    # Extract functions
    extractor = FunctionExtractor(source_code)
    extractor.visit(tree)
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"📂 Output directory: {output_dir}")
    print(f"🔍 Found {len(extractor.functions)} functions")
    print(f"📥 Found {len(extractor.imports)} import statements")
    
    if not extractor.functions:
        print("⚠️  No functions found in the file!")
        return True
    
    # Create function files
    for func_info in extractor.functions:
        print(f"  📝 Creating: {func_info['name']}.py")
        create_function_file(func_info, extractor.imports, output_dir, input_file)
    
    # Create summary file
    summary_file = output_dir / "_functions_summary.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# Functions Summary\n\n")
        f.write(f"**Source file:** `{input_file}`\n")
        f.write(f"**Date extracted:** {Path().cwd()}\n")
        f.write(f"**Total functions:** {len(extractor.functions)}\n\n")
        
        f.write("## Functions List\n\n")
        for func_info in extractor.functions:
            f.write(f"### `{func_info['name']}.py`\n")
            f.write(f"- **Type:** {'Async' if func_info['is_async'] else 'Regular'} function\n")
            f.write(f"- **Arguments:** {', '.join(func_info['args']) if func_info['args'] else 'None'}\n")
            f.write(f"- **Original line:** {func_info['start_line']}\n")
            if func_info['docstring']:
                f.write(f"- **Description:** {func_info['docstring'][:100]}{'...' if len(func_info['docstring']) > 100 else ''}\n")
            f.write("\n")
    
    print(f"✅ Successfully split {len(extractor.functions)} functions!")
    print(f"📋 Summary created: {summary_file}")
    return True


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Split Python file into separate function files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python split_functions.py                    # Split main.py (default)
    python split_functions.py myfile.py         # Split myfile.py
    python split_functions.py main.py -o funcs  # Custom output directory
        """
    )
    
    parser.add_argument(
        'input_file', 
        nargs='?', 
        default='main.py',
        help='Python file to split (default: main.py)'
    )
    
    parser.add_argument(
        '-o', '--output', 
        default='functions',
        help='Output directory for function files (default: functions)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    print("🐍 Python Function Splitter")
    print("=" * 40)
    
    # Check if input file exists
    if not Path(args.input_file).exists():
        print(f"❌ Error: Input file '{args.input_file}' does not exist!")
        print(f"💡 Current directory: {Path.cwd()}")
        print(f"📁 Available Python files:")
        for py_file in Path.cwd().glob("*.py"):
            print(f"   - {py_file.name}")
        return 1
    
    # Split the file
    success = split_python_file(args.input_file, args.output)
    
    if success:
        print("\n🎉 Done! Functions have been split successfully.")
        return 0
    else:
        print("\n❌ Failed to split functions.")
        return 1


if __name__ == "__main__":
    exit(main())

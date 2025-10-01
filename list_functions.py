#!/usr/bin/env python3
"""
Script to list all functions in a Python file
Usage: python3 list_functions.py <file_path>
"""

import ast
import sys
from pathlib import Path


class FunctionVisitor(ast.NodeVisitor):
    """AST visitor to collect function definitions"""
    
    def __init__(self):
        self.functions = []
        self.classes = {}
        self.current_class = None
    
    def visit_ClassDef(self, node):
        """Visit class definitions"""
        old_class = self.current_class
        self.current_class = node.name
        self.classes[node.name] = []
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        func_info = {
            'name': node.name,
            'line': node.lineno,
            'is_async': False,
            'class': self.current_class,
            'args': [arg.arg for arg in node.args.args],
            'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list]
        }
        
        if self.current_class:
            self.classes[self.current_class].append(func_info)
        else:
            self.functions.append(func_info)
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions"""
        func_info = {
            'name': node.name,
            'line': node.lineno,
            'is_async': True,
            'class': self.current_class,
            'args': [arg.arg for arg in node.args.args],
            'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list]
        }
        
        if self.current_class:
            self.classes[self.current_class].append(func_info)
        else:
            self.functions.append(func_info)
        
        self.generic_visit(node)
    
    def _get_decorator_name(self, decorator):
        """Extract decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return f"{decorator.func.value.id}.{decorator.func.attr}"
        return str(decorator)


def list_functions(file_path):
    """List all functions in a Python file"""
    
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ Error: File '{file_path}' not found")
        return
    
    if not path.suffix == '.py':
        print(f"⚠️  Warning: File '{file_path}' is not a Python file")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(path))
        visitor = FunctionVisitor()
        visitor.visit(tree)
        
        # Print results
        print("=" * 70)
        print(f"📄 File: {path}")
        print(f"📊 Total functions: {len(visitor.functions)}")
        print(f"📦 Total classes: {len(visitor.classes)}")
        print("=" * 70)
        
        # Print standalone functions
        if visitor.functions:
            print("\n🔧 STANDALONE FUNCTIONS:")
            print("-" * 70)
            for func in sorted(visitor.functions, key=lambda x: x['line']):
                async_marker = "async " if func['is_async'] else ""
                args_str = ", ".join(func['args']) if func['args'] else ""
                decorators_str = ""
                if func['decorators']:
                    decorators_str = f" [@{', @'.join(func['decorators'])}]"
                
                print(f"  Line {func['line']:4d}: {async_marker}def {func['name']}({args_str}){decorators_str}")
        
        # Print class methods
        if visitor.classes:
            print("\n📦 CLASS METHODS:")
            print("-" * 70)
            for class_name, methods in sorted(visitor.classes.items()):
                if methods:
                    print(f"\n  Class: {class_name}")
                    for method in sorted(methods, key=lambda x: x['line']):
                        async_marker = "async " if method['is_async'] else ""
                        args_str = ", ".join(method['args']) if method['args'] else ""
                        decorators_str = ""
                        if method['decorators']:
                            decorators_str = f" [@{', @'.join(method['decorators'])}]"
                        
                        print(f"    Line {method['line']:4d}: {async_marker}def {method['name']}({args_str}){decorators_str}")
        
        # Summary
        total_methods = sum(len(methods) for methods in visitor.classes.values())
        print("\n" + "=" * 70)
        print(f"📊 SUMMARY:")
        print(f"   Standalone functions: {len(visitor.functions)}")
        print(f"   Classes: {len(visitor.classes)}")
        print(f"   Class methods: {total_methods}")
        print(f"   Total: {len(visitor.functions) + total_methods}")
        print("=" * 70)
        
    except SyntaxError as e:
        print(f"❌ Syntax Error in file: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 list_functions.py <file_path>")
        print("\nExample:")
        print("  python3 list_functions.py main.py")
        print("  python3 list_functions.py modules/common/__init__.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    list_functions(file_path)


if __name__ == "__main__":
    main()

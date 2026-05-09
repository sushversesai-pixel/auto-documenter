# src/parser.py
import ast

class CodeParser(ast.NodeVisitor):
    """
    Traverses a Python Abstract Syntax Tree (AST) to extract information
    about classes, functions, and imports.
    """
    def __init__(self):
        self.symbols = []
        self.current_class = None
        self.dependencies = set()

    def visit_Import(self, node: ast.Import):
        """This method is called for each 'import X' statement."""
        for alias in node.names:
            self.dependencies.add(alias.name.split('.')[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """This method is called for each 'from X import Y' statement."""
        if node.module:
            self.dependencies.add(node.module.split('.')[0])
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """This method is called for each class definition."""
        class_info = {
            'type': 'class',
            'name': node.name,
            'methods': [],
            'code_block': ast.unparse(node)
        }
        self.symbols.append(class_info)
        self.current_class = class_info
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """This method is called for each function or method definition."""
        function_info = {
            'type': 'function',
            'name': node.name,
            'args': [arg.arg for arg in node.args.args],
            'return_type': ast.unparse(node.returns) if node.returns else 'None',
            'code_block': ast.unparse(node)
        }
        if self.current_class:
            function_info['type'] = 'method'
            self.current_class['methods'].append(function_info)
        else:
            self.symbols.append(function_info)
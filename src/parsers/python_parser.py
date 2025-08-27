"""
Python Code Parser

Uses Python's AST module to parse Python source code and extract
documentable elements like functions, classes, and modules.
"""

import ast
import os
import inspect
from typing import List, Optional, Any, Dict
from pathlib import Path

from models.code_elements import (
    CodeFunction, CodeClass, CodeModule, CodeParameter
)


class PythonParser:
    """Parser for Python source code using AST analysis."""
    
    def __init__(self):
        self.current_file = None
    
    def parse_file(self, file_path: str) -> List[Any]:
        """
        Parse a Python file and extract documentable elements.
        
        Args:
            file_path: Path to the Python file to parse
            
        Returns:
            List of CodeElement objects (functions, classes, modules)
        """
        self.current_file = file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source_code = file.read()
            
            # Parse the AST
            tree = ast.parse(source_code, filename=file_path)
            
            # Extract elements
            elements = []
            
            # Add module-level documentation
            module_element = self._parse_module(tree, file_path)
            if module_element:
                elements.append(module_element)
            
            # Visit AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_element = self._parse_function(node, source_code)
                    if func_element:
                        elements.append(func_element)
                
                elif isinstance(node, ast.AsyncFunctionDef):
                    func_element = self._parse_async_function(node, source_code)
                    if func_element:
                        elements.append(func_element)
                
                elif isinstance(node, ast.ClassDef):
                    class_element = self._parse_class(node, source_code)
                    if class_element:
                        elements.append(class_element)
            
            return elements
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
    
    def _parse_module(self, tree: ast.AST, file_path: str) -> Optional[CodeModule]:
        """Extract module-level information."""
        module_docstring = ast.get_docstring(tree)
        
        # Get module imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ''
                imports.extend([f"{module_name}.{alias.name}" for alias in node.names])
        
        return CodeModule(
            name=Path(file_path).stem,
            file_path=file_path,
            docstring=module_docstring,
            imports=imports[:10],  # Limit imports for readability
            line_number=1
        )
    
    def _parse_function(self, node: ast.FunctionDef, source_code: str) -> Optional[CodeFunction]:
        """Extract function information from AST node."""
        try:
            # Get function signature information
            parameters = self._extract_parameters(node.args)
            return_type = self._extract_return_type(node)
            decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
            
            # Get docstring
            docstring = ast.get_docstring(node)
            
            # Determine if function is private/public
            is_private = node.name.startswith('_')
            
            return CodeFunction(
                name=node.name,
                parameters=parameters,
                return_type=return_type,
                docstring=docstring,
                decorators=decorators,
                is_private=is_private,
                line_number=node.lineno,
                is_async=False,
                file_path=self.current_file
            )
            
        except Exception as e:
            print(f"Error parsing function {node.name}: {e}")
            return None
    
    def _parse_async_function(self, node: ast.AsyncFunctionDef, source_code: str) -> Optional[CodeFunction]:
        """Extract async function information from AST node."""
        func_element = self._parse_function(node, source_code)
        if func_element:
            func_element.is_async = True
        return func_element
    
    def _parse_class(self, node: ast.ClassDef, source_code: str) -> Optional[CodeClass]:
        """Extract class information from AST node."""
        try:
            # Get class docstring
            docstring = ast.get_docstring(node)
            
            # Get base classes
            base_classes = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_classes.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_classes.append(f"{base.value.id}.{base.attr}")
            
            # Get class methods
            methods = []
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method = self._parse_function(child, source_code)
                    if method:
                        methods.append(method)
            
            # Get class attributes (from __init__ and class level)
            attributes = self._extract_class_attributes(node)
            
            # Determine if class is private
            is_private = node.name.startswith('_')
            
            return CodeClass(
                name=node.name,
                base_classes=base_classes,
                methods=methods,
                attributes=attributes,
                docstring=docstring,
                is_private=is_private,
                line_number=node.lineno,
                file_path=self.current_file
            )
            
        except Exception as e:
            print(f"Error parsing class {node.name}: {e}")
            return None
    
    def _extract_parameters(self, args: ast.arguments) -> List[CodeParameter]:
        """Extract parameter information from function arguments."""
        parameters = []
        
        # Regular arguments
        for i, arg in enumerate(args.args):
            param_type = None
            default_value = None
            
            # Get type annotation
            if arg.annotation:
                param_type = self._get_type_annotation(arg.annotation)
            
            # Get default value
            defaults_offset = len(args.args) - len(args.defaults)
            if i >= defaults_offset:
                default_index = i - defaults_offset
                default_value = self._get_default_value(args.defaults[default_index])
            
            parameters.append(CodeParameter(
                name=arg.arg,
                param_type=param_type,
                default_value=default_value,
                is_required=default_value is None
            ))
        
        # Keyword-only arguments
        for i, arg in enumerate(args.kwonlyargs):
            param_type = None
            default_value = None
            
            if arg.annotation:
                param_type = self._get_type_annotation(arg.annotation)
            
            if i < len(args.kw_defaults) and args.kw_defaults[i]:
                default_value = self._get_default_value(args.kw_defaults[i])
            
            parameters.append(CodeParameter(
                name=arg.arg,
                param_type=param_type,
                default_value=default_value,
                is_required=default_value is None
            ))
        
        # *args
        if args.vararg:
            param_type = None
            if args.vararg.annotation:
                param_type = self._get_type_annotation(args.vararg.annotation)
            
            parameters.append(CodeParameter(
                name=f"*{args.vararg.arg}",
                param_type=param_type,
                default_value=None,
                is_required=False
            ))
        
        # **kwargs
        if args.kwarg:
            param_type = None
            if args.kwarg.annotation:
                param_type = self._get_type_annotation(args.kwarg.annotation)
            
            parameters.append(CodeParameter(
                name=f"**{args.kwarg.arg}",
                param_type=param_type,
                default_value=None,
                is_required=False
            ))
        
        return parameters
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation from function."""
        if node.returns:
            return self._get_type_annotation(node.returns)
        return None
    
    def _get_type_annotation(self, annotation: ast.AST) -> str:
        """Convert type annotation AST to string."""
        try:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Constant):
                return repr(annotation.value)
            elif isinstance(annotation, ast.Attribute):
                return f"{annotation.value.id}.{annotation.attr}"
            elif isinstance(annotation, ast.Subscript):
                value = self._get_type_annotation(annotation.value)
                slice_value = self._get_type_annotation(annotation.slice)
                return f"{value}[{slice_value}]"
            else:
                return ast.unparse(annotation)
        except:
            return "Any"
    
    def _get_default_value(self, default: ast.AST) -> str:
        """Extract default value from AST node."""
        try:
            if isinstance(default, ast.Constant):
                return repr(default.value)
            elif isinstance(default, ast.Name):
                return default.id
            elif isinstance(default, ast.Attribute):
                return f"{default.value.id}.{default.attr}"
            else:
                return ast.unparse(default)
        except:
            return "..."
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Extract decorator name from AST node."""
        try:
            if isinstance(decorator, ast.Name):
                return decorator.id
            elif isinstance(decorator, ast.Attribute):
                return f"{decorator.value.id}.{decorator.attr}"
            elif isinstance(decorator, ast.Call):
                return self._get_decorator_name(decorator.func)
            else:
                return ast.unparse(decorator)
        except:
            return "unknown"
    
    def _extract_class_attributes(self, node: ast.ClassDef) -> List[str]:
        """Extract class attributes from class definition."""
        attributes = []
        
        # Look for assignments at class level
        for child in node.body:
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
            elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                attributes.append(child.target.id)
        
        # Look for attributes in __init__ method
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == '__init__':
                for init_child in ast.walk(child):
                    if isinstance(init_child, ast.Assign):
                        for target in init_child.targets:
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                attributes.append(target.attr)
        
        return list(set(attributes))  # Remove duplicates

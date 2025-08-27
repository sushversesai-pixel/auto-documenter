"""
JavaScript/TypeScript Code Parser

Parses JavaScript and TypeScript source code to extract
documentable elements like functions, classes, and modules.
"""

import re
import json
import os
import subprocess
from typing import List, Optional, Any, Dict
from pathlib import Path

from models.code_elements import (
    CodeFunction, CodeClass, CodeModule, CodeParameter
)


class JavaScriptParser:
    """Parser for JavaScript and TypeScript source code."""
    
    def __init__(self):
        self.current_file = None
        
    def parse_file(self, file_path: str) -> List[Any]:
        """
        Parse a JavaScript/TypeScript file and extract documentable elements.
        
        Args:
            file_path: Path to the JS/TS file to parse
            
        Returns:
            List of CodeElement objects (functions, classes, modules)
        """
        self.current_file = file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source_code = file.read()
            
            elements = []
            
            # Add module-level documentation
            module_element = self._parse_module(source_code, file_path)
            if module_element:
                elements.append(module_element)
            
            # Parse functions
            functions = self._parse_functions(source_code)
            elements.extend(functions)
            
            # Parse classes
            classes = self._parse_classes(source_code)
            elements.extend(classes)
            
            # Parse arrow functions
            arrow_functions = self._parse_arrow_functions(source_code)
            elements.extend(arrow_functions)
            
            return elements
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
    
    def _parse_module(self, source_code: str, file_path: str) -> Optional[CodeModule]:
        """Extract module-level information."""
        # Extract file-level comments as module documentation
        module_docstring = self._extract_file_header_comment(source_code)
        
        # Extract imports
        imports = self._extract_imports(source_code)
        
        return CodeModule(
            name=Path(file_path).stem,
            file_path=file_path,
            docstring=module_docstring,
            imports=imports,
            line_number=1
        )
    
    def _parse_functions(self, source_code: str) -> List[CodeFunction]:
        """Parse regular function declarations."""
        functions = []
        
        # Regex for function declarations
        function_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^{]+))?\s*\{'
        
        for match in re.finditer(function_pattern, source_code, re.MULTILINE):
            function_name = match.group(1)
            params_str = match.group(2)
            return_type = match.group(3)
            
            # Find the line number
            line_number = source_code[:match.start()].count('\n') + 1
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Extract JSDoc comment
            docstring = self._extract_jsdoc_comment(source_code, match.start())
            
            # Check if async
            is_async = 'async' in match.group(0)
            
            functions.append(CodeFunction(
                name=function_name,
                parameters=parameters,
                return_type=return_type.strip() if return_type else None,
                docstring=docstring,
                decorators=[],
                is_private=function_name.startswith('_'),
                line_number=line_number,
                is_async=is_async,
                file_path=self.current_file
            ))
        
        return functions
    
    def _parse_arrow_functions(self, source_code: str) -> List[CodeFunction]:
        """Parse arrow function expressions."""
        functions = []
        
        # Regex for arrow functions assigned to variables/constants
        arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)(?:\s*:\s*([^=]+))?\s*=>\s*\{'
        
        for match in re.finditer(arrow_pattern, source_code, re.MULTILINE):
            function_name = match.group(1)
            params_str = match.group(2)
            return_type = match.group(3)
            
            # Find the line number
            line_number = source_code[:match.start()].count('\n') + 1
            
            # Parse parameters
            parameters = self._parse_parameters(params_str)
            
            # Extract JSDoc comment
            docstring = self._extract_jsdoc_comment(source_code, match.start())
            
            # Check if async
            is_async = 'async' in match.group(0)
            
            functions.append(CodeFunction(
                name=function_name,
                parameters=parameters,
                return_type=return_type.strip() if return_type else None,
                docstring=docstring,
                decorators=[],
                is_private=function_name.startswith('_'),
                line_number=line_number,
                is_async=is_async,
                file_path=self.current_file
            ))
        
        return functions
    
    def _parse_classes(self, source_code: str) -> List[CodeClass]:
        """Parse class declarations."""
        classes = []
        
        # Regex for class declarations
        class_pattern = r'(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        
        for match in re.finditer(class_pattern, source_code, re.MULTILINE):
            class_name = match.group(1)
            base_class = match.group(2)
            
            # Find the line number
            line_number = source_code[:match.start()].count('\n') + 1
            
            # Extract class body
            class_start = match.end()
            class_body = self._extract_class_body(source_code, class_start)
            
            # Parse methods
            methods = self._parse_class_methods(class_body)
            
            # Extract attributes (properties)
            attributes = self._extract_class_attributes(class_body)
            
            # Extract JSDoc comment
            docstring = self._extract_jsdoc_comment(source_code, match.start())
            
            classes.append(CodeClass(
                name=class_name,
                base_classes=[base_class] if base_class else [],
                methods=methods,
                attributes=attributes,
                docstring=docstring,
                is_private=class_name.startswith('_'),
                line_number=line_number,
                file_path=self.current_file
            ))
        
        return classes
    
    def _parse_parameters(self, params_str: str) -> List[CodeParameter]:
        """Parse function parameters from parameter string."""
        if not params_str.strip():
            return []
        
        parameters = []
        
        # Split parameters by comma, but handle nested types
        param_parts = self._split_parameters(params_str)
        
        for param in param_parts:
            param = param.strip()
            if not param:
                continue
                
            # Parse parameter with optional type and default value
            param_name = param
            param_type = None
            default_value = None
            is_required = True
            
            # Handle default values
            if '=' in param:
                param_part, default_value = param.split('=', 1)
                param = param_part.strip()
                default_value = default_value.strip()
                is_required = False
            
            # Handle type annotations
            if ':' in param:
                param_name, param_type = param.split(':', 1)
                param_name = param_name.strip()
                param_type = param_type.strip()
            
            # Handle optional parameters (?)
            if param_name.endswith('?'):
                param_name = param_name[:-1]
                is_required = False
            
            # Handle rest parameters
            if param_name.startswith('...'):
                param_name = param_name[3:]
                param_type = f"...{param_type}" if param_type else "...any"
            
            parameters.append(CodeParameter(
                name=param_name,
                param_type=param_type,
                default_value=default_value,
                is_required=is_required
            ))
        
        return parameters
    
    def _split_parameters(self, params_str: str) -> List[str]:
        """Split parameters by comma, handling nested brackets."""
        params = []
        current_param = ""
        bracket_depth = 0
        in_string = False
        string_char = None
        
        for char in params_str:
            if char in ['"', "'", '`'] and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            elif not in_string:
                if char in ['(', '[', '{']:
                    bracket_depth += 1
                elif char in [')', ']', '}']:
                    bracket_depth -= 1
                elif char == ',' and bracket_depth == 0:
                    params.append(current_param)
                    current_param = ""
                    continue
            
            current_param += char
        
        if current_param.strip():
            params.append(current_param)
        
        return params
    
    def _extract_class_body(self, source_code: str, class_start: int) -> str:
        """Extract the body of a class from the source code."""
        bracket_count = 1
        i = class_start
        
        while i < len(source_code) and bracket_count > 0:
            if source_code[i] == '{':
                bracket_count += 1
            elif source_code[i] == '}':
                bracket_count -= 1
            i += 1
        
        return source_code[class_start:i-1]
    
    def _parse_class_methods(self, class_body: str) -> List[CodeFunction]:
        """Parse methods from class body."""
        methods = []
        
        # Method patterns
        method_patterns = [
            r'(?:async\s+)?(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^{]+))?\s*\{',  # Regular methods
            r'(?:async\s+)?(get|set)\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^{]+))?\s*\{',  # Getters/setters
        ]
        
        for pattern in method_patterns:
            for match in re.finditer(pattern, class_body, re.MULTILINE):
                if len(match.groups()) == 3:  # Regular method
                    method_name = match.group(1)
                    params_str = match.group(2)
                    return_type = match.group(3)
                else:  # Getter/setter
                    method_type = match.group(1)
                    method_name = f"{method_type} {match.group(2)}"
                    params_str = match.group(3)
                    return_type = match.group(4) if len(match.groups()) > 3 else None
                
                # Parse parameters
                parameters = self._parse_parameters(params_str)
                
                # Extract JSDoc comment
                docstring = self._extract_jsdoc_comment(class_body, match.start())
                
                # Check if async
                is_async = 'async' in match.group(0)
                
                methods.append(CodeFunction(
                    name=method_name,
                    parameters=parameters,
                    return_type=return_type.strip() if return_type else None,
                    docstring=docstring,
                    decorators=[],
                    is_private=method_name.startswith('_'),
                    line_number=1,  # Relative to class
                    is_async=is_async,
                    file_path=self.current_file
                ))
        
        return methods
    
    def _extract_class_attributes(self, class_body: str) -> List[str]:
        """Extract class attributes/properties."""
        attributes = []
        
        # Property declarations
        property_pattern = r'(?:public|private|protected)?\s*(\w+)(?:\?)?(?:\s*:\s*[^;=]+)?(?:\s*=\s*[^;]+)?;'
        
        for match in re.finditer(property_pattern, class_body):
            attr_name = match.group(1)
            if attr_name not in ['constructor', 'function', 'class']:
                attributes.append(attr_name)
        
        # Also look for this.property assignments
        this_pattern = r'this\.(\w+)\s*='
        
        for match in re.finditer(this_pattern, class_body):
            attr_name = match.group(1)
            if attr_name not in attributes:
                attributes.append(attr_name)
        
        return attributes
    
    def _extract_jsdoc_comment(self, source_code: str, position: int) -> Optional[str]:
        """Extract JSDoc comment before the given position."""
        # Look backwards for JSDoc comment
        before_code = source_code[:position]
        
        # Find the last JSDoc comment block
        jsdoc_pattern = r'/\*\*(.*?)\*/'
        matches = list(re.finditer(jsdoc_pattern, before_code, re.DOTALL))
        
        if matches:
            last_match = matches[-1]
            # Check if the comment is close to the position (within 3 lines)
            lines_between = before_code[last_match.end():].count('\n')
            if lines_between <= 3:
                comment_text = last_match.group(1)
                # Clean up the comment
                lines = comment_text.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('*'):
                        line = line[1:].strip()
                    if line:
                        cleaned_lines.append(line)
                return '\n'.join(cleaned_lines)
        
        return None
    
    def _extract_file_header_comment(self, source_code: str) -> Optional[str]:
        """Extract file header comment/documentation."""
        lines = source_code.split('\n')
        header_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            elif line.startswith('//'):
                header_lines.append(line[2:].strip())
            elif line.startswith('/*'):
                # Handle block comments
                if line.endswith('*/'):
                    header_lines.append(line[2:-2].strip())
                else:
                    # Multi-line block comment
                    in_comment = True
                    comment_content = line[2:].strip()
                    if comment_content:
                        header_lines.append(comment_content)
                    continue
            elif line.startswith('*') and len(header_lines) > 0:
                header_lines.append(line[1:].strip())
            elif line.endswith('*/'):
                header_lines.append(line[:-2].strip())
                break
            else:
                # Non-comment line, stop collecting header
                break
        
        return '\n'.join(header_lines) if header_lines else None
    
    def _extract_imports(self, source_code: str) -> List[str]:
        """Extract import statements."""
        imports = []
        
        # ES6 imports
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'const\s+.*?\s+=\s+require\([\'"]([^\'"]+)[\'"]\)',
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, source_code, re.MULTILINE):
                imports.append(match.group(1))
        
        return imports[:10]  # Limit to first 10 imports

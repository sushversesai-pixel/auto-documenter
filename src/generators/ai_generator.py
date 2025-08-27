"""
AI-Powered Documentation Generator

Uses OpenAI's GPT models to generate intelligent documentation
for code elements including docstrings, summaries, and examples.
"""

import json
import os
from typing import List, Dict, Any, Optional
from openai import OpenAI

from models.code_elements import CodeFunction, CodeClass, CodeModule


class AIGenerator:
    """AI-powered generator for code documentation."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the AI generator.
        
        Args:
            config: Configuration dictionary with OpenAI settings
        """
        self.config = config or {}
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
        )
        
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        self.model = self.config.get('model', 'gpt-5')
        self.max_tokens = self.config.get('max_tokens', 1000)
        self.temperature = self.config.get('temperature', 0.3)
    
    def generate_documentation(self, elements: List[Any], language: str, style: str) -> Dict[str, Any]:
        """
        Generate documentation for a list of code elements.
        
        Args:
            elements: List of CodeElement objects to document
            language: Programming language (python, javascript, etc.)
            style: Documentation style (google, numpy, sphinx, jsdoc)
            
        Returns:
            Dictionary containing generated documentation for each element
        """
        documentation = {}
        
        for element in elements:
            try:
                if isinstance(element, CodeFunction):
                    doc = self._generate_function_documentation(element, language, style)
                elif isinstance(element, CodeClass):
                    doc = self._generate_class_documentation(element, language, style)
                elif isinstance(element, CodeModule):
                    doc = self._generate_module_documentation(element, language, style)
                else:
                    continue
                
                documentation[f"{element.name}_{element.line_number}"] = doc
                
            except Exception as e:
                print(f"Error generating documentation for {element.name}: {e}")
                continue
        
        return documentation
    
    def _generate_function_documentation(self, func: CodeFunction, language: str, style: str) -> Dict[str, Any]:
        """Generate documentation for a function."""
        # Create context for the AI
        context = {
            'name': func.name,
            'parameters': [{'name': p.name, 'type': p.param_type, 'default': p.default_value, 'required': p.is_required} for p in func.parameters],
            'return_type': func.return_type,
            'is_async': func.is_async,
            'decorators': func.decorators,
            'existing_docstring': func.docstring,
            'language': language,
            'style': style
        }
        
        # Generate documentation using AI
        prompt = self._create_function_documentation_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert technical writer specializing in {language} documentation. "
                                 f"Generate clear, comprehensive documentation following {style} style guidelines. "
                                 f"Always respond with valid JSON in the specified format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Add metadata
            result['element_type'] = 'function'
            result['language'] = language
            result['style'] = style
            
            return result
            
        except Exception as e:
            print(f"AI generation failed for function {func.name}: {e}")
            return self._generate_fallback_function_doc(func, style)
    
    def _generate_class_documentation(self, cls: CodeClass, language: str, style: str) -> Dict[str, Any]:
        """Generate documentation for a class."""
        context = {
            'name': cls.name,
            'base_classes': cls.base_classes,
            'methods': [{'name': m.name, 'parameters': [p.name for p in m.parameters]} for m in cls.methods],
            'attributes': cls.attributes,
            'existing_docstring': cls.docstring,
            'language': language,
            'style': style
        }
        
        prompt = self._create_class_documentation_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert technical writer specializing in {language} documentation. "
                                 f"Generate clear, comprehensive class documentation following {style} style guidelines. "
                                 f"Always respond with valid JSON in the specified format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            result = json.loads(response.choices[0].message.content)
            result['element_type'] = 'class'
            result['language'] = language
            result['style'] = style
            
            return result
            
        except Exception as e:
            print(f"AI generation failed for class {cls.name}: {e}")
            return self._generate_fallback_class_doc(cls, style)
    
    def _generate_module_documentation(self, module: CodeModule, language: str, style: str) -> Dict[str, Any]:
        """Generate documentation for a module."""
        context = {
            'name': module.name,
            'file_path': module.file_path,
            'imports': module.imports,
            'existing_docstring': module.docstring,
            'language': language,
            'style': style
        }
        
        prompt = self._create_module_documentation_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert technical writer specializing in {language} documentation. "
                                 f"Generate clear, comprehensive module documentation. "
                                 f"Always respond with valid JSON in the specified format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            result = json.loads(response.choices[0].message.content)
            result['element_type'] = 'module'
            result['language'] = language
            result['style'] = style
            
            return result
            
        except Exception as e:
            print(f"AI generation failed for module {module.name}: {e}")
            return self._generate_fallback_module_doc(module, style)
    
    def generate_module_readme(self, module_structure: Dict, language: str) -> str:
        """Generate a README for a module/package."""
        prompt = f"""
        Generate a comprehensive README.md content for a {language} module with the following structure:
        
        Module Information:
        - Language: {language}
        - Total files: {module_structure.get('total_files', 0)}
        - Sample modules: {', '.join(module_structure.get('modules', [])[:5])}
        
        Create a README that includes:
        1. Module overview and purpose
        2. Installation instructions
        3. Usage examples
        4. API reference summary
        5. Contributing guidelines
        
        Return the content as markdown text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical writer. Generate clear, professional README content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.4
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"AI generation failed for module README: {e}")
            return self._generate_fallback_readme(module_structure, language)
    
    def _create_function_documentation_prompt(self, context: Dict) -> str:
        """Create a prompt for function documentation generation."""
        return f"""
        Generate comprehensive documentation for the following {context['language']} function:
        
        Function: {context['name']}
        Parameters: {json.dumps(context['parameters'], indent=2)}
        Return Type: {context.get('return_type', 'Not specified')}
        Is Async: {context.get('is_async', False)}
        Decorators: {context.get('decorators', [])}
        Existing Documentation: {context.get('existing_docstring', 'None')}
        
        Generate documentation in {context['style']} style with the following JSON format:
        {{
            "summary": "Brief description of what the function does",
            "description": "Detailed description of the function's behavior",
            "parameters": [
                {{
                    "name": "parameter_name",
                    "type": "parameter_type",
                    "description": "Parameter description",
                    "required": true/false
                }}
            ],
            "returns": {{
                "type": "return_type",
                "description": "Description of return value"
            }},
            "raises": [
                {{
                    "exception": "ExceptionType",
                    "description": "When this exception is raised"
                }}
            ],
            "examples": [
                {{
                    "code": "example_usage_code",
                    "description": "Example description"
                }}
            ],
            "notes": ["Any additional notes or considerations"]
        }}
        """
    
    def _create_class_documentation_prompt(self, context: Dict) -> str:
        """Create a prompt for class documentation generation."""
        return f"""
        Generate comprehensive documentation for the following {context['language']} class:
        
        Class: {context['name']}
        Base Classes: {context.get('base_classes', [])}
        Methods: {json.dumps(context.get('methods', []), indent=2)}
        Attributes: {context.get('attributes', [])}
        Existing Documentation: {context.get('existing_docstring', 'None')}
        
        Generate documentation in {context['style']} style with the following JSON format:
        {{
            "summary": "Brief description of the class purpose",
            "description": "Detailed description of the class functionality",
            "attributes": [
                {{
                    "name": "attribute_name",
                    "type": "attribute_type",
                    "description": "Attribute description"
                }}
            ],
            "methods_summary": "Brief overview of key methods",
            "examples": [
                {{
                    "code": "example_usage_code",
                    "description": "Example description"
                }}
            ],
            "notes": ["Any additional notes about the class"]
        }}
        """
    
    def _create_module_documentation_prompt(self, context: Dict) -> str:
        """Create a prompt for module documentation generation."""
        return f"""
        Generate comprehensive documentation for the following {context['language']} module:
        
        Module: {context['name']}
        File Path: {context.get('file_path', '')}
        Imports: {context.get('imports', [])}
        Existing Documentation: {context.get('existing_docstring', 'None')}
        
        Generate documentation with the following JSON format:
        {{
            "summary": "Brief description of the module purpose",
            "description": "Detailed description of the module functionality",
            "main_features": ["List of main features or capabilities"],
            "dependencies": ["Key dependencies based on imports"],
            "usage_examples": [
                {{
                    "code": "example_import_and_usage",
                    "description": "Example description"
                }}
            ],
            "notes": ["Any additional notes about the module"]
        }}
        """
    
    def _generate_fallback_function_doc(self, func: CodeFunction, style: str) -> Dict[str, Any]:
        """Generate fallback documentation when AI fails."""
        return {
            'summary': f"Function {func.name}",
            'description': func.docstring or f"Implementation of {func.name} function.",
            'parameters': [
                {
                    'name': p.name,
                    'type': p.param_type or 'Any',
                    'description': f"Parameter {p.name}",
                    'required': p.is_required
                } for p in func.parameters
            ],
            'returns': {
                'type': func.return_type or 'Any',
                'description': 'Return value'
            },
            'element_type': 'function',
            'language': 'unknown',
            'style': style
        }
    
    def _generate_fallback_class_doc(self, cls: CodeClass, style: str) -> Dict[str, Any]:
        """Generate fallback documentation when AI fails."""
        return {
            'summary': f"Class {cls.name}",
            'description': cls.docstring or f"Implementation of {cls.name} class.",
            'attributes': [
                {
                    'name': attr,
                    'type': 'Any',
                    'description': f"Attribute {attr}"
                } for attr in cls.attributes
            ],
            'methods_summary': f"Contains {len(cls.methods)} methods",
            'element_type': 'class',
            'language': 'unknown',
            'style': style
        }
    
    def _generate_fallback_module_doc(self, module: CodeModule, style: str) -> Dict[str, Any]:
        """Generate fallback documentation when AI fails."""
        return {
            'summary': f"Module {module.name}",
            'description': module.docstring or f"Implementation of {module.name} module.",
            'main_features': ['Core functionality'],
            'dependencies': module.imports[:5],
            'element_type': 'module',
            'language': 'unknown',
            'style': style
        }
    
    def _generate_fallback_readme(self, module_structure: Dict, language: str) -> str:
        """Generate fallback README when AI fails."""
        return f"""# {language.title()} Module

## Overview

This {language} module contains {module_structure.get('total_files', 0)} files.

## Files

{chr(10).join([f"- {module}" for module in module_structure.get('modules', [])[:10]])}

## Installation

Install dependencies and run the module according to your project setup.

## Usage

Import and use the module components as needed.

## Contributing

Follow standard {language} development practices.
"""

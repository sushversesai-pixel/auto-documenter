"""
Template-based Documentation Generator

Generates formatted documentation using Jinja2 templates
for different output formats and documentation styles.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template


class TemplateGenerator:
    """Template-based generator for formatted documentation."""
    
    def __init__(self, style: str = 'google'):
        """
        Initialize the template generator.
        
        Args:
            style: Documentation style (google, numpy, sphinx, jsdoc)
        """
        self.style = style
        
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent.parent / 'templates'
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['title_case'] = self._title_case
        self.env.filters['snake_to_title'] = self._snake_to_title
    
    def generate_file_documentation(self, elements: List[Any], ai_docs: Dict[str, Any], 
                                   file_path: str) -> str:
        """
        Generate complete documentation for a single file.
        
        Args:
            elements: List of code elements in the file
            ai_docs: AI-generated documentation for each element
            file_path: Relative path of the source file
            
        Returns:
            Formatted markdown documentation
        """
        try:
            # Organize elements by type
            functions = [e for e in elements if e.type == 'function']
            classes = [e for e in elements if e.type == 'class']
            modules = [e for e in elements if e.type == 'module']
            
            # Create template context
            context = {
                'file_path': file_path,
                'functions': functions,
                'classes': classes,
                'modules': modules,
                'ai_docs': ai_docs,
                'style': self.style,
                'total_elements': len(elements)
            }
            
            # Load and render template
            template = self.env.get_template('api_reference.md')
            return template.render(context)
            
        except Exception as e:
            print(f"Template generation failed for {file_path}: {e}")
            return self._generate_fallback_file_doc(elements, file_path)
    
    def generate_function_docstring(self, func_data: Dict[str, Any]) -> str:
        """
        Generate a docstring for a function based on AI documentation.
        
        Args:
            func_data: AI-generated function documentation
            
        Returns:
            Formatted docstring text
        """
        try:
            context = {
                'doc': func_data,
                'style': self.style
            }
            
            template = self.env.get_template('function_docstring.md')
            return template.render(context)
            
        except Exception as e:
            print(f"Function docstring generation failed: {e}")
            return self._generate_fallback_docstring(func_data)
    
    def generate_class_docstring(self, class_data: Dict[str, Any]) -> str:
        """
        Generate a docstring for a class based on AI documentation.
        
        Args:
            class_data: AI-generated class documentation
            
        Returns:
            Formatted docstring text
        """
        try:
            context = {
                'doc': class_data,
                'style': self.style
            }
            
            template = self.env.get_template('class_docstring.md')
            return template.render(context)
            
        except Exception as e:
            print(f"Class docstring generation failed: {e}")
            return self._generate_fallback_docstring(class_data)
    
    def generate_module_readme(self, module_structure: Dict, ai_content: str) -> str:
        """
        Generate a README file for a module.
        
        Args:
            module_structure: Module structure information
            ai_content: AI-generated README content
            
        Returns:
            Formatted README markdown
        """
        try:
            context = {
                'module': module_structure,
                'ai_content': ai_content,
                'style': self.style
            }
            
            template = self.env.get_template('module_readme.md')
            return template.render(context)
            
        except Exception as e:
            print(f"Module README generation failed: {e}")
            return ai_content or self._generate_fallback_readme(module_structure)
    
    def generate_api_reference(self, languages: List[str]) -> str:
        """
        Generate an API reference index.
        
        Args:
            languages: List of programming languages documented
            
        Returns:
            Formatted API reference index
        """
        context = {
            'languages': languages,
            'style': self.style
        }
        
        content = f"""# API Reference

This documentation was auto-generated using AI-powered code analysis.

## Supported Languages

{chr(10).join([f"- [{lang.title()}]({lang}/)" for lang in languages])}

## Documentation Style

Documentation follows {self.style} style guidelines.

## Navigation

Browse the documentation by language and module. Each section includes:

- Function and method documentation
- Class definitions and usage
- Module overviews and dependencies
- Usage examples and code snippets

## Last Updated

This documentation is automatically updated with code changes.
"""
        return content
    
    def _title_case(self, text: str) -> str:
        """Convert text to title case."""
        return text.replace('_', ' ').title()
    
    def _snake_to_title(self, text: str) -> str:
        """Convert snake_case to Title Case."""
        return text.replace('_', ' ').title()
    
    def _generate_fallback_file_doc(self, elements: List[Any], file_path: str) -> str:
        """Generate fallback documentation when template fails."""
        content = [f"# {file_path}\n"]
        
        for element in elements:
            content.append(f"## {element.type.title()}: {element.name}\n")
            if hasattr(element, 'docstring') and element.docstring:
                content.append(f"{element.docstring}\n")
            else:
                content.append(f"No documentation available for {element.name}.\n")
            content.append("")
        
        return "\n".join(content)
    
    def _generate_fallback_docstring(self, data: Dict[str, Any]) -> str:
        """Generate fallback docstring when template fails."""
        summary = data.get('summary', 'No description available.')
        description = data.get('description', '')
        
        if description and description != summary:
            return f"{summary}\n\n{description}"
        return summary
    
    def _generate_fallback_readme(self, module_structure: Dict) -> str:
        """Generate fallback README when template fails."""
        language = module_structure.get('language', 'Unknown')
        total_files = module_structure.get('total_files', 0)
        
        return f"""# {language.title()} Module

## Overview

This module contains {total_files} source files.

## Structure

The module is organized into the following components:

- Core functionality
- Utility functions  
- Configuration and setup

## Usage

Import the module components as needed for your application.
"""

# Code Auto-Documenter

## Overview

Code Auto-Documenter is an AI-powered CLI tool that automatically generates comprehensive documentation for Python and JavaScript/TypeScript codebases. The tool leverages OpenAI's GPT-5 model to intelligently analyze source code using Abstract Syntax Tree (AST) parsing and generate documentation in multiple formats and styles. It supports various documentation standards (Google, NumPy, Sphinx, JSDoc) and provides Git integration for automated documentation workflows.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### CLI Architecture
The application uses a command-line interface built with the Click framework, providing a main entry point through `main.py` that delegates to the CLI module. The CLI supports various commands for generating documentation with configurable options for output format, style, and target languages.

### Parser Architecture
The system employs language-specific parsers that use AST analysis to extract code elements:
- **PythonParser**: Uses Python's built-in `ast` module for parsing Python source code
- **JavaScriptParser**: Implements custom parsing logic for JavaScript/TypeScript files using regex patterns and subprocess calls

Each parser extracts structured information about functions, classes, modules, and parameters into standardized data models.

### Documentation Generation Pipeline
The architecture follows a two-stage generation process:
1. **AI Generation**: Uses OpenAI's GPT-5 model to generate intelligent documentation content based on extracted code elements
2. **Template Generation**: Applies Jinja2 templates to format the AI-generated content into structured documentation following specific style guides

### Data Model Design
The system uses a dataclass-based approach with inheritance for representing code elements:
- Base `CodeElement` class with common properties
- Specialized classes for `CodeFunction`, `CodeClass`, `CodeModule`, and `CodeParameter`
- Type hints and optional fields for flexible data representation

### Template System
Jinja2-based templating engine supports multiple documentation styles and output formats:
- Style-specific templates for Google, NumPy, Sphinx, and JSDoc formats
- Modular template structure for functions, classes, and API references
- Custom filters for text transformation and formatting

### Git Integration
Built-in Git integration provides:
- Repository detection and validation
- Pre-commit hook installation for automated documentation updates
- Change tracking for selective documentation regeneration

### File Management
Centralized file utilities handle:
- Directory traversal with configurable ignore patterns
- Source file discovery based on file extensions
- Path resolution and validation across different operating systems

## External Dependencies

### AI Services
- **OpenAI API**: Primary dependency for GPT-5 model access, requiring API key authentication for documentation generation

### Core Python Libraries
- **Click**: Command-line interface framework for CLI argument parsing and command structure
- **PyYAML**: Configuration file parsing for user-defined settings and preferences
- **Jinja2**: Template engine for generating formatted documentation output
- **GitPython**: Git repository interaction and hook management
- **Pathlib**: Modern path handling and file system operations

### Development Tools
- **Git**: Version control integration for repository detection and hook installation
- **AST Module**: Built-in Python module for Abstract Syntax Tree parsing of Python source code

### Optional Dependencies
- **Subprocess**: For executing external commands, particularly for JavaScript/TypeScript parsing
- **JSON**: For handling configuration data and structured output formatting
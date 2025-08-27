# Code Auto-Documenter

An AI-powered CLI tool that automatically generates comprehensive documentation for Python and JavaScript codebases using OpenAI's GPT models.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-green.svg)

## 🚀 Features

- **Multi-language Support**: Generate documentation for Python and JavaScript/TypeScript
- **AI-Powered**: Uses OpenAI's GPT-5 model for intelligent documentation generation
- **Multiple Style Guides**: Supports Google, NumPy, Sphinx, and JSDoc documentation styles
- **AST-based Parsing**: Accurate code analysis using Abstract Syntax Trees
- **Git Integration**: Pre-commit hooks for automatic documentation updates
- **Flexible Output**: Generate Markdown and HTML documentation
- **CLI Interface**: Easy-to-use command-line interface

## 📋 Requirements

- Python 3.8 or higher
- OpenAI API key
- Git (for hook integration)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd code-auto-documenter
   ```

2. **Install Python dependencies:**
   ```bash
   pip install openai click pyyaml jinja2 gitpython pathlib
   ```

3. **Set up your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## 🎯 Quick Start

### Basic Usage

Generate documentation for a Python project:

```bash
python main.py generate /path/to/your/project --output ./docs

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()

# Configure the Gemini client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_docstring(symbol_info: dict) -> str:
    """Generates a docstring for a function or method using Gemini."""
    prompt = f"""
    Generate a complete Google-style Python docstring for the following {symbol_info['type']}.
    The docstring must include a summary, an 'Args:' section for all arguments, and a 'Returns:' section.
    Only return the docstring itself, enclosed in triple quotes. Do not return the function signature.

    Code:
    {symbol_info['code_block']}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f'"""Error generating docstring: {e}"""'

def generate_module_readme(symbols: list, module_name: str) -> str:
    """Generates a README summary for a module using Gemini."""
    prompt = f"""
    Generate a README in Markdown format for a Python module named '{module_name}'.
    The module contains these classes and functions: {[s['name'] for s in symbols]}.
    The README should have a one-paragraph summary of the module's purpose and a list
    of its main components.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"# {module_name}\n\nError generating README: {e}"

def generate_architecture_diagram(dependencies: set, module_name: str) -> str:
    """Generates a Mermaid.js dependency diagram."""
    if not dependencies:
        return ""
    
    mermaid_code = "graph TD;\n"
    for dep in dependencies:
        if dep != module_name:
            mermaid_code += f"    {module_name} --> {dep};\n"
    
    return f"""
## Architecture Diagram
This diagram shows the top-level dependencies of the `{module_name}` module.

```mermaid
{mermaid_code}
"""
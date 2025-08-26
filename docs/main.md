# src/main.py
import typer
import ast
import subprocess
from pathlib import Path

from .parser import CodeParser
from .generator import generate_docstring, generate_module_readme, generate_architecture_diagram

# [cite_start]Initialize the command-line application using Typer [cite: 53]
app = typer.Typer()

@app.command()
def generate(
    target_path: Path = typer.Argument(..., help="Path to the Python file or directory to document."),
    output_dir: Path = typer.Option("docs", help="Directory to save the documentation files.")
):
    """
    Parses a Python codebase, generates documentation, and prepares it for publishing.
    [cite_start]This is part of the core end-to-end pipeline[cite: 37].
    """
    output_dir.mkdir(exist_ok=True)
    
    if target_path.is_file() and target_path.suffix == '.py':
        files_to_process = [target_path]
    elif target_path.is_dir():
        files_to_process = list(target_path.rglob("*.py"))
    else:
        print(f"Error: Invalid target path '{target_path}'. Please provide a Python file or a directory.")
        raise typer.Exit(code=1)

    all_symbols = []
    all_dependencies = set()
    for filepath in files_to_process:
        # Skip files in virtual environments or cache folders
        if ".venv" in str(filepath) or "__pycache__" in str(filepath):
            continue

        print(f"📄 Processing: {filepath}...")
        try:
            # Read the source code file using UTF-8 encoding
            source_code = filepath.read_text(encoding="utf-8")
            
            # [cite_start]Parse the code using AST to extract symbols [cite: 15]
            tree = ast.parse(source_code)
            parser = CodeParser()
            parser.visit(tree)
            
            all_symbols.extend(parser.symbols)
            all_dependencies.update(parser.dependencies)

            # [cite_start]Generate LLM-powered docstrings for each symbol [cite: 16]
            markdown_content = f"# Documentation for `{filepath.name}`\n\n"
            for symbol in parser.symbols:
                if symbol['type'] == 'class':
                    markdown_content += f"## Class: `{symbol['name']}`\n"
                    for method in symbol.get('methods', []):
                        docstring = generate_docstring(method)
                        markdown_content += f"### Method: `{method['name']}`\n```python\n{docstring}\n```\n\n"
                elif symbol['type'] == 'function':
                    docstring = generate_docstring(symbol)
                    markdown_content += f"## Function: `{symbol['name']}`\n```python\n{docstring}\n```\n\n"
            
            # [cite_start]Write the documentation to a Markdown file [cite: 20]
            md_filename = output_dir / f"{filepath.stem}.md"
            md_filename.write_text(markdown_content, encoding="utf-8")
            print(f"   ✔️ Saved docstrings to {md_filename}")
        except Exception as e:
            print(f"   ❌ Error processing {filepath}: {e}")

    if target_path.is_dir():
        # [cite_start]Generate a README for the entire module/directory [cite: 17]
        print("   - Generating project README...")
        readme_content = generate_module_readme(all_symbols, target_path.name)
        readme_path = output_dir / "index.md"
        readme_path.write_text(readme_content, encoding="utf-8")
        print(f"✔️ Project README saved to {readme_path}")

        # [cite_start]Generate the architecture diagram [cite: 22, 42]
        print("   - Generating architecture diagram...")
        diagram_content = generate_architecture_diagram(all_dependencies, target_path.name)
        if diagram_content:
            diagram_path = output_dir / "architecture.md"
            diagram_path.write_text(diagram_content, encoding="utf-8")
            print(f"✔️ Architecture diagram saved to {diagram_path}")


@app.command()
def publish(
    docs_dir: Path = typer.Option("docs", help="Directory containing the documentation files.")
):
    """
    [cite_start]Builds the MkDocs site from the generated documentation, creating the final HTML output[cite: 39, 40].
    """
    mkdocs_config = f"""
site_name: AI-Generated Documentation
theme:
  name: material
nav:
  - Home: index.md
  - Architecture: architecture.md
"""
    
    config_path = Path("mkdocs.yml")
    config_path.write_text(mkdocs_config, encoding="utf-8")
    
    print("Building documentation site with MkDocs...")
    subprocess.run(["mkdocs", "build"], check=True, shell=True)
    print("✔️ Site built successfully in the 'site' directory!")


if __name__ == "__main__":
    app()


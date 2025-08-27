# src/main.py
import typer
import ast
import subprocess
from pathlib import Path

from .parser import CodeParser
from .generator import generate_docstring, generate_module_readme, generate_architecture_diagram

app = typer.Typer()

@app.command()
def generate(
    target_path: Path = typer.Argument(..., help="Path to the Python file or directory to document."),
    output_dir: Path = typer.Option("docs", help="Directory to save the documentation files.")
):
    """Generates AI-powered documentation for a Python codebase."""
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
        if ".venv" in str(filepath) or "__pycache__" in str(filepath):
            continue

        print(f"📄 Processing: {filepath}...")
        try:
            source_code = filepath.read_text(encoding="utf-8")
            
            tree = ast.parse(source_code)
            parser = CodeParser()
            parser.visit(tree)
            
            all_symbols.extend(parser.symbols)
            all_dependencies.update(parser.dependencies)

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
            
            md_filename = output_dir / f"{filepath.stem}.md"
            md_filename.write_text(markdown_content, encoding="utf-8")
            print(f"   ✔️ Saved docstrings to {md_filename}")
        except Exception as e:
            print(f"   ❌ Error processing {filepath}: {e}")

    if target_path.is_dir():
        print("   - Generating project README...")
        readme_content = generate_module_readme(all_symbols, target_path.name)
        readme_path = output_dir / "index.md"
        readme_path.write_text(readme_content, encoding="utf-8")
        print(f"✔️ Project README saved to {readme_path}")

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
    """Builds the MkDocs site from the generated documentation."""
    
    # --- NEW ROBUST LOGIC ---
    # Start building the navigation string
    nav_string = "nav:\n  - Home: index.md\n"
    
    # Check if architecture.md exists and add it
    architecture_file = docs_dir / "architecture.md"
    if architecture_file.exists():
        nav_string += "  - Architecture: architecture.md\n"

    # Dynamically find all other markdown files and add them
    api_files = sorted([f.name for f in docs_dir.glob("*.md") if f.name not in ["index.md", "architecture.md"]])
    if api_files:
        nav_string += "  - API Reference:\n"
        for md_file in api_files:
            # Capitalize the name for the nav, e.g., 'main.md' -> 'Main'
            page_name = md_file.replace('.md', '').capitalize()
            nav_string += f"      - {page_name}: {md_file}\n"

    mkdocs_config = f"""
site_name: AI-Generated Documentation
theme:
  name: material
{nav_string}
"""
    
    config_path = Path("mkdocs.yml")
    config_path.write_text(mkdocs_config, encoding)
    
    print("Building documentation site with MkDocs...")
    subprocess.run(["mkdocs", "build", "--verbose"], check=True, shell=True)
    print("✔️ Site built successfully in the 'site' directory!")

if __name__ == "__main__":
    app()

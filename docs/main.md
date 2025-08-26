# Documentation for `main.py`

## Function: `generate`
```python
```python
"""Generates AI-powered documentation for a Python codebase.

Args:
    target_path: Path to the Python file or directory to document.
    output_dir: Directory to save the documentation files. Defaults to 'docs'.

Returns:
    None.  The function generates markdown documentation files in the specified output directory.  It prints messages indicating progress and any errors encountered.
"""
```
```

## Function: `publish`
```python
```python
"""Builds the MkDocs site from the generated documentation.

Args:
    docs_dir: Path to the directory containing the documentation files. Defaults to 'docs'.

Returns:
    None.  The function prints messages indicating build progress and success, 
    and creates the 'site' directory containing the built MkDocs site.  
    It raises a subprocess.CalledProcessError if the 'mkdocs build' command fails.
"""
```
```


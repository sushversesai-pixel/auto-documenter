"""
File Utilities

Provides utility functions for file operations, directory traversal,
and source code file management.
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple


class FileUtils:
    """Utility class for file and directory operations."""
    
    def __init__(self):
        # Common patterns to ignore during file scanning
        self.ignore_patterns = {
            'directories': {
                '__pycache__', '.git', '.svn', '.hg', '.bzr',
                'node_modules', '.vscode', '.idea', '.vs',
                'build', 'dist', '.coverage', '.pytest_cache',
                '.mypy_cache', '.tox', 'venv', 'env'
            },
            'files': {
                '*.pyc', '*.pyo', '*.pyd', '*.so', '*.egg',
                '*.log', '*.tmp', '*.temp', '.DS_Store',
                'Thumbs.db', '*.min.js', '*.bundle.js'
            }
        }
    
    def find_source_files(self, root_path: str, extensions: List[str]) -> List[str]:
        """
        Find all source files with given extensions in a directory tree.
        
        Args:
            root_path: Root directory to search in
            extensions: List of file extensions to include (e.g., ['.py', '.js'])
            
        Returns:
            List of absolute paths to source files
        """
        source_files = []
        root_path_obj = Path(root_path).resolve()
        
        for file_path in self._walk_directory(root_path_obj):
            if file_path.suffix.lower() in [ext.lower() for ext in extensions]:
                if not self._should_ignore_file(file_path):
                    source_files.append(str(file_path))
        
        return sorted(source_files)
    
    def _walk_directory(self, root_path: Path):
        """
        Walk directory tree, yielding file paths while respecting ignore patterns.
        
        Args:
            root_path: Root directory to walk
            
        Yields:
            Path objects for each file found
        """
        for current_dir, dirs, files in os.walk(root_path):
            current_path = Path(current_dir)
            
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore_directory(d)]
            
            # Yield file paths
            for file_name in files:
                file_path = current_path / file_name
                yield file_path
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored based on patterns.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be ignored, False otherwise
        """
        file_name = file_path.name
        
        # Check against file patterns
        for pattern in self.ignore_patterns['files']:
            if fnmatch.fnmatch(file_name, pattern):
                return True
        
        # Check if any parent directory should be ignored
        for part in file_path.parts:
            if part in self.ignore_patterns['directories']:
                return True
        
        return False
    
    def _should_ignore_directory(self, dir_name: str) -> bool:
        """
        Check if a directory should be ignored.
        
        Args:
            dir_name: Name of the directory
            
        Returns:
            True if directory should be ignored, False otherwise
        """
        return dir_name in self.ignore_patterns['directories']
    
    def build_directory_tree(self, root_path: str, extensions: Optional[List[str]] = None) -> Dict:
        """
        Build a directory tree structure with file counts.
        
        Args:
            root_path: Root directory to analyze
            extensions: Optional list of extensions to filter by
            
        Returns:
            Dictionary representing the directory tree
        """
        root_path_obj = Path(root_path).resolve()
        tree = {
            'name': root_path_obj.name,
            'path': str(root_path_obj),
            'type': 'directory',
            'children': [],
            'file_count': 0
        }
        
        # Get all files if extensions not specified
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
        
        # Build tree structure
        self._build_tree_recursive(root_path_obj, tree, extensions)
        
        return tree
    
    def _build_tree_recursive(self, path: Path, node: Dict, extensions: List[str]):
        """
        Recursively build directory tree structure.
        
        Args:
            path: Current path being processed
            node: Current node in the tree
            extensions: File extensions to include
        """
        try:
            items = sorted(path.iterdir())
        except PermissionError:
            return
        
        for item in items:
            if self._should_ignore_file(item):
                continue
            
            if item.is_dir():
                if not self._should_ignore_directory(item.name):
                    child_node = {
                        'name': item.name,
                        'path': str(item),
                        'type': 'directory',
                        'children': [],
                        'file_count': 0
                    }
                    
                    self._build_tree_recursive(item, child_node, extensions)
                    
                    # Add child if it has files or subdirectories
                    if child_node['file_count'] > 0 or child_node['children']:
                        node['children'].append(child_node)
                        node['file_count'] += child_node['file_count']
            
            elif item.suffix.lower() in [ext.lower() for ext in extensions]:
                child_node = {
                    'name': item.name,
                    'path': str(item),
                    'type': 'file',
                    'size': item.stat().st_size
                }
                
                node['children'].append(child_node)
                node['file_count'] += 1
    
    def get_file_info(self, file_path: str) -> Dict:
        """
        Get detailed information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file information
        """
        path = Path(file_path)
        
        if not path.exists():
            return {'exists': False}
        
        stat = path.stat()
        
        info = {
            'exists': True,
            'name': path.name,
            'stem': path.stem,
            'suffix': path.suffix,
            'size': stat.st_size,
            'modified_time': stat.st_mtime,
            'is_file': path.is_file(),
            'is_directory': path.is_dir(),
            'absolute_path': str(path.resolve()),
            'relative_path': str(path)
        }
        
        # Add line count for text files
        if path.is_file() and path.suffix.lower() in ['.py', '.js', '.ts', '.jsx', '.tsx', '.md', '.txt']:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    info['line_count'] = sum(1 for _ in f)
            except (UnicodeDecodeError, PermissionError):
                info['line_count'] = None
        
        return info
    
    def create_output_directory(self, output_path: str) -> bool:
        """
        Create output directory structure.
        
        Args:
            output_path: Path where documentation will be generated
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(output_path)
            path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for different languages
            (path / 'python').mkdir(exist_ok=True)
            (path / 'javascript').mkdir(exist_ok=True)
            (path / 'assets').mkdir(exist_ok=True)
            
            return True
            
        except Exception as e:
            print(f"Error creating output directory: {e}")
            return False
    
    def backup_existing_docs(self, docs_path: str) -> Optional[str]:
        """
        Create a backup of existing documentation.
        
        Args:
            docs_path: Path to existing documentation
            
        Returns:
            Path to backup directory if successful, None otherwise
        """
        docs_path_obj = Path(docs_path)
        
        if not docs_path_obj.exists():
            return None
        
        try:
            import shutil
            import time
            
            timestamp = int(time.time())
            backup_path = docs_path_obj.parent / f"{docs_path_obj.name}_backup_{timestamp}"
            
            shutil.copytree(docs_path_obj, backup_path)
            return str(backup_path)
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def get_project_structure_summary(self, root_path: str) -> Dict:
        """
        Get a summary of the project structure.
        
        Args:
            root_path: Root directory of the project
            
        Returns:
            Dictionary containing project structure summary
        """
        python_files = self.find_source_files(root_path, ['.py'])
        js_files = self.find_source_files(root_path, ['.js', '.ts', '.jsx', '.tsx'])
        
        summary = {
            'root_path': root_path,
            'total_python_files': len(python_files),
            'total_js_files': len(js_files),
            'total_files': len(python_files) + len(js_files),
            'languages': [],
            'largest_files': [],
            'directory_count': 0
        }
        
        if python_files:
            summary['languages'].append('python')
        if js_files:
            summary['languages'].append('javascript')
        
        # Get largest files
        all_files = python_files + js_files
        file_sizes = []
        
        for file_path in all_files:
            try:
                size = os.path.getsize(file_path)
                file_sizes.append((file_path, size))
            except OSError:
                continue
        
        # Sort by size and get top 5
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        summary['largest_files'] = [
            {
                'path': os.path.relpath(path, root_path),
                'size': size
            }
            for path, size in file_sizes[:5]
        ]
        
        # Count directories
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_directory(d)]
            summary['directory_count'] += len(dirs)
        
        return summary
    
    def safe_write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        Safely write content to a file with error handling.
        
        Args:
            file_path: Path where to write the file
            content: Content to write
            encoding: File encoding to use
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first
            temp_path = path.with_suffix(path.suffix + '.tmp')
            
            with open(temp_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Atomically replace the original file
            temp_path.replace(path)
            
            return True
            
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            return False

"""
Git Integration Utilities

Provides functionality for integrating with Git repositories,
setting up hooks, and managing documentation in version control.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any


class GitIntegration:
    """Handles Git repository integration and hook management."""
    
    def __init__(self):
        self.git_available = self._check_git_availability()
    
    def _check_git_availability(self) -> bool:
        """Check if Git is available on the system."""
        try:
            subprocess.run(['git', '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def is_git_repository(self, path: str) -> bool:
        """
        Check if the given path is a Git repository.
        
        Args:
            path: Path to check
            
        Returns:
            True if it's a Git repository, False otherwise
        """
        if not self.git_available:
            return False
        
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=path,
                capture_output=True,
                check=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False
    
    def setup_pre_commit_hook(self, repo_path: str) -> bool:
        """
        Set up a pre-commit hook for automatic documentation updates.
        
        Args:
            repo_path: Path to the Git repository
            
        Returns:
            True if setup successful, False otherwise
        """
        if not self.is_git_repository(repo_path):
            print(f"Error: {repo_path} is not a Git repository")
            return False
        
        hooks_dir = Path(repo_path) / '.git' / 'hooks'
        pre_commit_path = hooks_dir / 'pre-commit'
        
        # Create hooks directory if it doesn't exist
        hooks_dir.mkdir(exist_ok=True)
        
        # Read the pre-commit hook template
        template_path = Path(__file__).parent.parent.parent / 'hooks' / 'pre-commit'
        
        try:
            if template_path.exists():
                shutil.copy2(template_path, pre_commit_path)
            else:
                # Create a basic pre-commit hook if template doesn't exist
                hook_content = self._create_basic_pre_commit_hook()
                with open(pre_commit_path, 'w') as f:
                    f.write(hook_content)
            
            # Make the hook executable
            pre_commit_path.chmod(0o755)
            
            print(f"✅ Pre-commit hook installed at {pre_commit_path}")
            return True
            
        except Exception as e:
            print(f"Error setting up pre-commit hook: {e}")
            return False
    
    def get_changed_files(self, repo_path: str, file_extensions: List[str] = None) -> List[str]:
        """
        Get list of changed files in the repository.
        
        Args:
            repo_path: Path to the Git repository
            file_extensions: List of file extensions to filter (e.g., ['.py', '.js'])
            
        Returns:
            List of changed file paths
        """
        if not self.is_git_repository(repo_path):
            return []
        
        try:
            # Get staged files
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                cwd=repo_path,
                capture_output=True,
                check=True,
                text=True
            )
            
            changed_files = result.stdout.strip().split('\n')
            changed_files = [f for f in changed_files if f]  # Remove empty strings
            
            # Filter by extensions if provided
            if file_extensions:
                filtered_files = []
                for file_path in changed_files:
                    if any(file_path.endswith(ext) for ext in file_extensions):
                        full_path = os.path.join(repo_path, file_path)
                        if os.path.exists(full_path):
                            filtered_files.append(full_path)
                changed_files = filtered_files
            else:
                changed_files = [os.path.join(repo_path, f) for f in changed_files]
            
            return changed_files
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting changed files: {e}")
            return []
    
    def stage_documentation_files(self, repo_path: str, doc_files: List[str]) -> bool:
        """
        Stage documentation files for commit.
        
        Args:
            repo_path: Path to the Git repository
            doc_files: List of documentation file paths to stage
            
        Returns:
            True if staging successful, False otherwise
        """
        if not self.is_git_repository(repo_path):
            return False
        
        try:
            for doc_file in doc_files:
                if os.path.exists(doc_file):
                    relative_path = os.path.relpath(doc_file, repo_path)
                    subprocess.run(
                        ['git', 'add', relative_path],
                        cwd=repo_path,
                        check=True
                    )
            
            print(f"✅ Staged {len(doc_files)} documentation files")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error staging documentation files: {e}")
            return False
    
    def get_repository_info(self, repo_path: str) -> Dict[str, Any]:
        """
        Get information about the Git repository.
        
        Args:
            repo_path: Path to the Git repository
            
        Returns:
            Dictionary containing repository information
        """
        info = {
            'is_git_repo': False,
            'branch': None,
            'remote_url': None,
            'last_commit': None
        }
        
        if not self.is_git_repository(repo_path):
            return info
        
        info['is_git_repo'] = True
        
        try:
            # Get current branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                check=True,
                text=True
            )
            info['branch'] = result.stdout.strip()
            
            # Get remote URL
            result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                info['remote_url'] = result.stdout.strip()
            
            # Get last commit
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H %s'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                info['last_commit'] = result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not get some repository info: {e}")
        
        return info
    
    def create_documentation_branch(self, repo_path: str, branch_name: str = 'docs-auto-update') -> bool:
        """
        Create a new branch for documentation updates.
        
        Args:
            repo_path: Path to the Git repository
            branch_name: Name of the branch to create
            
        Returns:
            True if branch creation successful, False otherwise
        """
        if not self.is_git_repository(repo_path):
            return False
        
        try:
            # Check if branch already exists
            result = subprocess.run(
                ['git', 'rev-parse', '--verify', branch_name],
                cwd=repo_path,
                capture_output=True
            )
            
            if result.returncode == 0:
                # Branch exists, check it out
                subprocess.run(['git', 'checkout', branch_name], cwd=repo_path, check=True)
            else:
                # Create and checkout new branch
                subprocess.run(['git', 'checkout', '-b', branch_name], cwd=repo_path, check=True)
            
            print(f"✅ Working on branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating documentation branch: {e}")
            return False
    
    def _create_basic_pre_commit_hook(self) -> str:
        """Create a basic pre-commit hook script."""
        return """#!/bin/bash
# Auto-generated pre-commit hook for code documentation

echo "🚀 Running code auto-documenter..."

# Check if we have any Python or JavaScript files staged
has_python=$(git diff --cached --name-only | grep -E '\\.py$' | wc -l)
has_js=$(git diff --cached --name-only | grep -E '\\.(js|ts|jsx|tsx)$' | wc -l)

if [ "$has_python" -gt 0 ] || [ "$has_js" -gt 0 ]; then
    # Run the documentation generator
    if command -v python3 &> /dev/null && [ -f "main.py" ]; then
        echo "📝 Generating documentation..."
        python3 main.py generate . --output ./docs --verbose
        
        if [ $? -eq 0 ]; then
            echo "✅ Documentation updated successfully"
            
            # Stage the generated documentation files
            git add docs/
            
        else
            echo "❌ Documentation generation failed"
            echo "Commit will proceed without documentation updates"
        fi
    else
        echo "⚠️ Code auto-documenter not found, skipping documentation update"
    fi
else
    echo "ℹ️ No Python or JavaScript files changed, skipping documentation update"
fi

echo "✅ Pre-commit hook completed"
exit 0
"""

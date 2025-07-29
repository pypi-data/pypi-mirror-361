"""
Git utilities for diff-based scanning and repository operations.
"""

import subprocess
import platform
from pathlib import Path
from typing import List, Optional
import git

class GitUtils:
    """Utility class for git operations."""
    
    @staticmethod
    def is_git_repo(path: Path) -> bool:
        """Check if the given path is a git repository."""
        try:
            git.Repo(path)
            return True
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            return False
    
    @staticmethod
    def get_modified_files(repo_path: Path) -> List[Path]:
        """Get list of modified files in the git repository."""
        try:
            repo = git.Repo(repo_path)
            
            # Get staged changes
            staged_files = []
            for diff in repo.index.diff('HEAD'):
                if diff.a_path:
                    staged_files.append(repo_path / diff.a_path)
                if diff.b_path:
                    staged_files.append(repo_path / diff.b_path)
            
            # Get unstaged changes
            unstaged_files = []
            for diff in repo.index.diff(None):
                if diff.a_path:
                    unstaged_files.append(repo_path / diff.a_path)
                if diff.b_path:
                    unstaged_files.append(repo_path / diff.b_path)
            
            # Get untracked files
            untracked_files = []
            for untracked in repo.untracked_files:
                untracked_files.append(repo_path / untracked)
            
            # Combine all modified files
            all_files = set(staged_files + unstaged_files + untracked_files)
            
            # Filter out directories and non-existent files
            valid_files = []
            for file_path in all_files:
                if file_path.exists() and file_path.is_file():
                    valid_files.append(file_path)
            
            return valid_files
        
        except Exception as e:
            print(f"Error getting modified files: {e}")
            return []
    
    @staticmethod
    def get_diff_content(repo_path: Path, file_path: Path) -> Optional[str]:
        """Get the diff content for a specific file."""
        try:
            repo = git.Repo(repo_path)
            
            # Get the diff for the file
            diff = repo.git.diff('HEAD', str(file_path), ignore_blank_lines=True)
            
            if not diff:
                # Check if it's a new file
                if file_path in repo.untracked_files:
                    # Return the content of the new file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
            
            return diff
        
        except Exception as e:
            print(f"Error getting diff content for {file_path}: {e}")
            return None
    
    @staticmethod
    def get_commit_files(repo_path: Path, commit_hash: str) -> List[Path]:
        """Get list of files changed in a specific commit."""
        try:
            repo = git.Repo(repo_path)
            commit = repo.commit(commit_hash)
            
            files = []
            for diff in commit.diff(commit.parents[0] if commit.parents else git.NULL_TREE):
                if diff.a_path:
                    files.append(repo_path / diff.a_path)
                if diff.b_path:
                    files.append(repo_path / diff.b_path)
            
            return [f for f in files if f.exists() and f.is_file()]
        
        except Exception as e:
            print(f"Error getting commit files: {e}")
            return []
    
    @staticmethod
    def get_branch_files(repo_path: Path, branch_name: str) -> List[Path]:
        """Get list of files that differ between current branch and specified branch."""
        try:
            repo = git.Repo(repo_path)
            
            # Get diff between current branch and specified branch
            diff = repo.git.diff(branch_name, '--name-only')
            
            files = []
            for file_path in diff.split('\n'):
                if file_path.strip():
                    full_path = repo_path / file_path.strip()
                    if full_path.exists() and full_path.is_file():
                        files.append(full_path)
            
            return files
        
        except Exception as e:
            print(f"Error getting branch files: {e}")
            return []
    
    @staticmethod
    def get_repo_info(repo_path: Path) -> dict:
        """Get repository information."""
        try:
            repo = git.Repo(repo_path)
            
            return {
                'repo_path': str(repo_path),
                'active_branch': repo.active_branch.name,
                'remote_url': repo.remotes.origin.url if repo.remotes else None,
                'last_commit': {
                    'hash': repo.head.commit.hexsha[:8],
                    'message': repo.head.commit.message.strip(),
                    'author': repo.head.commit.author.name,
                    'date': repo.head.commit.committed_datetime.isoformat()
                },
                'is_dirty': repo.is_dirty(),
                'untracked_files': len(repo.untracked_files),
                'staged_files': len(repo.index.diff('HEAD')),
                'unstaged_files': len(repo.index.diff(None))
            }
        
        except Exception as e:
            print(f"Error getting repo info: {e}")
            return {}
    
    @staticmethod
    def create_patch(repo_path: Path, file_path: Path) -> Optional[str]:
        """Create a patch for a specific file."""
        try:
            repo = git.Repo(repo_path)
            
            # Create patch for the file
            patch = repo.git.diff('HEAD', str(file_path))
            
            return patch if patch else None
        
        except Exception as e:
            print(f"Error creating patch for {file_path}: {e}")
            return None
    
    @staticmethod
    def get_file_history(repo_path: Path, file_path: Path, max_commits: int = 10) -> List[dict]:
        """Get commit history for a specific file."""
        try:
            repo = git.Repo(repo_path)
            
            # Get log for the file
            log = repo.git.log('--oneline', f'-{max_commits}', '--', str(file_path))
            
            commits = []
            for line in log.split('\n'):
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        commits.append({
                            'hash': parts[0],
                            'message': parts[1]
                        })
            
            return commits
        
        except Exception as e:
            print(f"Error getting file history for {file_path}: {e}")
            return [] 
"""
Pre-commit hook utilities for theSecrect scanner.
"""

import os
import stat
import platform
import subprocess
from pathlib import Path
from typing import Optional

class PreCommitHook:
    """Manage pre-commit hooks for Secrect scanning."""
    
    def __init__(self):
        self.hook_content_bash = self._get_hook_content_bash()
        self.hook_content_batch = self._get_hook_content_batch()
        self.hook_content_python = self._get_hook_content_python()
    
    def install(self, repo_path: str = ".", force: bool = False) -> bool:
        """Install pre-commit hook in the specified repository."""
        repo_path = Path(repo_path).resolve()
        hooks_dir = repo_path / ".git" / "hooks"
        hook_file = hooks_dir / "pre-commit"
        
        # Check if it's a git repository
        if not (repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")
        
        # Check if hook already exists
        if hook_file.exists() and not force:
            return False
        
        # Create hooks directory if it doesn't exist
        hooks_dir.mkdir(parents=True, exist_ok=True)
        
        # Choose appropriate hook content based on platform
        if platform.system() == "Windows":
            hook_content = self.hook_content_batch
            hook_file = hook_file.with_suffix('.bat')
        else:
            hook_content = self.hook_content_bash
        
        # Write hook content
        with open(hook_file, 'w', newline='\n') as f:
            f.write(hook_content)
        
        # Make hook executable (Unix-like systems only)
        if platform.system() != "Windows":
            hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
        
        return True
    
    def uninstall(self, repo_path: str = ".") -> bool:
        """Uninstall pre-commit hook from the specified repository."""
        repo_path = Path(repo_path).resolve()
        
        # Check for both .bat and regular hook files
        hook_files = [
            repo_path / ".git" / "hooks" / "pre-commit",
            repo_path / ".git" / "hooks" / "pre-commit.bat"
        ]
        
        for hook_file in hook_files:
            if hook_file.exists():
                # Check if it's our hook
                try:
                    with open(hook_file, 'r') as f:
                        content = f.read()
                    
                    if "Secret & PII Scanner" in content:
                        # Remove the hook
                        hook_file.unlink()
                        return True
                except:
                    continue
        
        return False
    
    def _get_hook_content_bash(self) -> str:
        """Get the content for the bash pre-commit hook."""
        return '''#!/bin/bash
#Secrect & PII Scanner Pre-commit Hook
# This hook runs theSecrect scanner on modified files before each commit

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Change to repository root
cd "$REPO_ROOT"

# Check ifSecrect scanner is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not available. Cannot runSecrect scanner."
    exit 1
fi

# Try to find theSecrect scanner script
SCANNER_SCRIPT=""
for script in "secret_scanner.py" "secret-scanner.py" "secret_scanner/secret_scanner.py"; do
    if [ -f "$script" ]; then
        SCANNER_SCRIPT="$script"
        break
    fi
done

if [ -z "$SCANNER_SCRIPT" ]; then
    echo "❌Secrect scanner script not found. Please install theSecrect scanner first."
    echo "   Expected locations:Secrect_scanner.py,Secrect-scanner.py, orSecrect_scanner/secret_scanner.py"
    exit 1
fi

echo "🔐 RunningSecrect & PII Scanner on modified files..."

# Run the scanner on modified files only
if python3 "$SCANNER_SCRIPT" scan . --diff-only --exit-on-failure --quiet 2>/dev/null || python "$SCANNER_SCRIPT" scan . --diff-only --exit-on-failure --quiet 2>/dev/null; then
    echo "✅Secrect scan passed. Proceeding with commit."
    exit 0
else
    echo ""
    echo "❌Secrect scan failed! PotentialSecrects or PII found."
    echo ""
    echo "Please review the findings above and:"
    echo "  1. Remove or replace any hardcodedSecrects"
    echo "  2. Use environment variables for sensitive data"
    echo "  3. Add files to .gitignore if they contain test data"
    echo ""
    echo "To bypass this check (not recommended), use:"
    echo "  git commit --no-verify"
    echo ""
    exit 1
fi
'''
    
    def _get_hook_content_batch(self) -> str:
        """Get the content for the Windows batch pre-commit hook."""
        return '''@echo off
REMSecrect & PII Scanner Pre-commit Hook
REM This hook runs theSecrect scanner on modified files before each commit

REM Get the repository root
for /f "tokens=*" %%i in ('git rev-parse --show-toplevel') do set REPO_ROOT=%%i

REM Change to repository root
cd /d "%REPO_ROOT%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python is not available. Cannot runSecrect scanner.
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

REM Try to find theSecrect scanner script
set SCANNER_SCRIPT=
if exist "secrect_scanner.py" (
    set SCANNER_SCRIPT=secrect_scanner.py
) else if exist "secret-scanner.py" (
    set SCANNER_SCRIPT=secret-scanner.py
) else if exist "secrect_scanner\secrect_scanner.py" (
    set SCANNER_SCRIPT=secrect_scanner\secrect_scanner.py
)

if "%SCANNER_SCRIPT%"=="" (
    echo ❌Secrect scanner script not found. Please install theSecrect scanner first.
    echo    Expected locations:Secrect_scanner.py,Secrect-scanner.py, orSecrect_scanner\secret_scanner.py
    exit /b 1
)

echo 🔐 RunningSecrect ^& PII Scanner on modified files...

REM Run the scanner on modified files only
%PYTHON_CMD% "%SCANNER_SCRIPT%" scan . --diff-only --exit-on-failure --quiet
if errorlevel 1 (
    echo.
    echo ❌Secrect scan failed! PotentialSecrects or PII found.
    echo.
    echo Please review the findings above and:
    echo   1. Remove or replace any hardcodedSecrects
    echo   2. Use environment variables for sensitive data
    echo   3. Add files to .gitignore if they contain test data
    echo.
    echo To bypass this check (not recommended), use:
    echo   git commit --no-verify
    echo.
    exit /b 1
) else (
    echo ✅Secrect scan passed. Proceeding with commit.
    exit /b 0
)
'''
    
    def _get_hook_content_python(self) -> str:
        """Get the content for a Python-based pre-commit hook (most portable)."""
        return '''#!/usr/bin/env python3
"""
Secret & PII Scanner Pre-commit Hook
This hook runs theSecrect scanner on modified files before each commit
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get repository root
    try:
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], 
                              capture_output=True, text=True, check=True)
        repo_root = Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("❌ Not a git repository or git not available.")
        sys.exit(1)
    
    # Change to repository root
    os.chdir(repo_root)
    
    # Check if Python is available
    python_cmd = None
    for cmd in ['python3', 'python']:
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
            python_cmd = cmd
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    if not python_cmd:
        print("❌ Python is not available. Cannot runSecrect scanner.")
        sys.exit(1)
    
    # Try to find theSecrect scanner script
    scanner_script = None
    for script in ['secret_scanner.py', 'secret-scanner.py', 'secret_scanner/secret_scanner.py']:
        if Path(script).exists():
            scanner_script = script
            break
    
    if not scanner_script:
        print("❌Secrect scanner script not found. Please install theSecrect scanner first.")
        print("   Expected locations:Secrect_scanner.py,Secrect-scanner.py, orSecrect_scanner/secret_scanner.py")
        sys.exit(1)
    
    print("🔐 RunningSecrect & PII Scanner on modified files...")
    
    # Run the scanner on modified files only
    try:
        subprocess.run([python_cmd, scanner_script, 'scan', '.', '--diff-only', '--exit-on-failure', '--quiet'], 
                      check=True)
        print("✅Secrect scan passed. Proceeding with commit.")
        sys.exit(0)
    except subprocess.CalledProcessError:
        print()
        print("❌Secrect scan failed! PotentialSecrects or PII found.")
        print()
        print("Please review the findings above and:")
        print("  1. Remove or replace any hardcodedSecrects")
        print("  2. Use environment variables for sensitive data")
        print("  3. Add files to .gitignore if they contain test data")
        print()
        print("To bypass this check (not recommended), use:")
        print("  git commit --no-verify")
        print()
        sys.exit(1)

if __name__ == '__main__':
    main()
'''
    
    def is_installed(self, repo_path: str = ".") -> bool:
        """Check if the pre-commit hook is installed."""
        repo_path = Path(repo_path).resolve()
        
        # Check for both .bat and regular hook files
        hook_files = [
            repo_path / ".git" / "hooks" / "pre-commit",
            repo_path / ".git" / "hooks" / "pre-commit.bat"
        ]
        
        for hook_file in hook_files:
            if hook_file.exists():
                # Check if it's our hook
                try:
                    with open(hook_file, 'r') as f:
                        content = f.read()
                    if "Secret & PII Scanner" in content:
                        return True
                except:
                    continue
        
        return False
    
    def get_hook_status(self, repo_path: str = ".") -> dict:
        """Get detailed status of the pre-commit hook."""
        repo_path = Path(repo_path).resolve()
        
        # Check for both .bat and regular hook files
        hook_files = [
            repo_path / ".git" / "hooks" / "pre-commit",
            repo_path / ".git" / "hooks" / "pre-commit.bat"
        ]
        
        status = {
            'installed': False,
            'is_git_repo': (repo_path / ".git").exists(),
            'hook_exists': False,
            'is_executable': False,
            'is_our_hook': False,
            'hook_path': None,
            'platform': platform.system()
        }
        
        if not status['is_git_repo']:
            return status
        
        for hook_file in hook_files:
            if hook_file.exists():
                status['hook_exists'] = True
                status['hook_path'] = str(hook_file)
                
                # Check if executable (Unix-like systems only)
                if platform.system() != "Windows":
                    try:
                        stat_info = hook_file.stat()
                        status['is_executable'] = bool(stat_info.st_mode & stat.S_IEXEC)
                    except:
                        pass
                
                # Check if it's our hook
                try:
                    with open(hook_file, 'r') as f:
                        content = f.read()
                    status['is_our_hook'] = "Secret & PII Scanner" in content
                    status['installed'] = status['is_our_hook']
                except:
                    pass
                
                break
        
        return status
    
    def create_global_hook(self, global_hooks_dir: Optional[str] = None) -> bool:
        """Create a global git hook template."""
        if global_hooks_dir is None:
            # Try to find global hooks directory
            try:
                result = subprocess.run(['git', 'config', '--global', 'core.hooksPath'], 
                                      capture_output=True, text=True, check=True)
                global_hooks_dir = result.stdout.strip()
            except subprocess.CalledProcessError:
                # Default global hooks directory
                home = Path.home()
                global_hooks_dir = str(home / ".git-templates" / "hooks")
        
        global_hooks_path = Path(global_hooks_dir)
        global_hooks_path.mkdir(parents=True, exist_ok=True)
        
        # Choose appropriate hook content based on platform
        if platform.system() == "Windows":
            hook_content = self.hook_content_batch
            hook_file = global_hooks_path / "pre-commit.bat"
        else:
            hook_content = self.hook_content_bash
            hook_file = global_hooks_path / "pre-commit"
        
        # Write hook content
        with open(hook_file, 'w', newline='\n') as f:
            f.write(hook_content)
        
        # Make executable (Unix-like systems only)
        if platform.system() != "Windows":
            hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
        
        # Set global hooks path
        try:
            subprocess.run(['git', 'config', '--global', 'core.hooksPath', global_hooks_dir], 
                          check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def test_hook(self, repo_path: str = ".") -> bool:
        """Test the pre-commit hook by running it manually."""
        repo_path = Path(repo_path).resolve()
        
        # Check if hook exists
        hook_files = [
            repo_path / ".git" / "hooks" / "pre-commit",
            repo_path / ".git" / "hooks" / "pre-commit.bat"
        ]
        
        hook_file = None
        for hf in hook_files:
            if hf.exists():
                hook_file = hf
                break
        
        if not hook_file:
            return False
        
        # Run the hook
        try:
            if platform.system() == "Windows":
                result = subprocess.run([str(hook_file)], capture_output=True, text=True)
            else:
                result = subprocess.run(['bash', str(hook_file)], capture_output=True, text=True)
            
            return result.returncode == 0
        except Exception:
            return False 
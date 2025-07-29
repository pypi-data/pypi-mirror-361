"""
Platform utilities for cross-platform compatibility.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple

def get_system_info() -> dict:
    """Get system information for compatibility checks."""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
    }

def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"

def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == "Darwin"

def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system() == "Linux"

def get_python_command() -> str:
    """Get the appropriate Python command for the current platform."""
    # Try python3 first, then python
    for cmd in ['python3', 'python']:
        try:
            subprocess.run([cmd, '--version'], 
                         capture_output=True, check=True, timeout=5)
            return cmd
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    # Fallback to python if nothing else works
    return 'python'

def get_git_command() -> str:
    """Get the appropriate git command for the current platform."""
    try:
        subprocess.run(['git', '--version'], 
                      capture_output=True, check=True, timeout=5)
        return 'git'
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        raise RuntimeError("Git is not available on this system")

def normalize_path(path: str) -> str:
    """Normalize path for cross-platform compatibility."""
    return str(Path(path).resolve())

def get_home_directory() -> Path:
    """Get the home directory in a cross-platform way."""
    return Path.home()

def get_temp_directory() -> Path:
    """Get the temporary directory in a cross-platform way."""
    return Path(os.environ.get('TEMP', os.environ.get('TMP', '/tmp')))

def make_executable(file_path: Path) -> bool:
    """Make a file executable (Unix-like systems only)."""
    if is_windows():
        return True  # No need on Windows
    
    try:
        current_mode = file_path.stat().st_mode
        file_path.chmod(current_mode | 0o755)
        return True
    except Exception:
        return False

def run_command_safely(command: List[str], 
                      timeout: int = 30,
                      capture_output: bool = True,
                      text: bool = True,
                      cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """
    Run a command safely with proper error handling.
    
    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=text,
            timeout=timeout,
            cwd=cwd,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout} seconds"
    except FileNotFoundError:
        return -1, "", f"Command not found: {command[0]}"
    except Exception as e:
        return -1, "", f"Error running command: {str(e)}"

def get_file_encoding(file_path: Path) -> str:
    """Detect file encoding for safe reading."""
    try:
        # Try UTF-8 first
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Read a small sample
        return 'utf-8'
    except UnicodeDecodeError:
        try:
            # Try with error handling
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.read(1024)
            return 'utf-8'
        except Exception:
            # Fallback to system default
            return 'latin-1'

def safe_read_file(file_path: Path, max_size: int = 10 * 1024 * 1024) -> Optional[str]:
    """
    Safely read a file with proper error handling and size limits.
    
    Args:
        file_path: Path to the file to read
        max_size: Maximum file size in bytes (default: 10MB)
    
    Returns:
        File content as string, or None if file cannot be read
    """
    try:
        # Check file size
        if file_path.stat().st_size > max_size:
            return None
        
        # Detect encoding
        encoding = get_file_encoding(file_path)
        
        # Read file
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            return f.read()
    
    except (OSError, IOError, UnicodeDecodeError):
        return None

def get_platform_specific_paths() -> dict:
    """Get platform-specific paths and configurations."""
    system = platform.system()
    
    if system == "Windows":
        return {
            'home': Path.home(),
            'temp': Path(os.environ.get('TEMP', os.environ.get('TMP', 'C:\\Temp'))),
            'git_hooks_template': Path.home() / ".git-templates" / "hooks",
            'python_cmd': 'python',
            'path_separator': '\\',
            'line_ending': '\r\n'
        }
    elif system == "Darwin":  # macOS
        return {
            'home': Path.home(),
            'temp': Path('/tmp'),
            'git_hooks_template': Path.home() / ".git-templates" / "hooks",
            'python_cmd': 'python3',
            'path_separator': '/',
            'line_ending': '\n'
        }
    else:  # Linux and others
        return {
            'home': Path.home(),
            'temp': Path('/tmp'),
            'git_hooks_template': Path.home() / ".git-templates" / "hooks",
            'python_cmd': 'python3',
            'path_separator': '/',
            'line_ending': '\n'
        }

def check_dependencies() -> dict:
    """Check if required dependencies are available."""
    dependencies = {
        'python': False,
        'git': False,
        'weasyprint': False,
        'reportlab': False
    }
    
    # Check Python
    try:
        import sys
        dependencies['python'] = True
    except ImportError:
        pass
    
    # Check Git
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, timeout=5)
        dependencies['git'] = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Check WeasyPrint
    try:
        import weasyprint
        dependencies['weasyprint'] = True
    except ImportError:
        pass
    
    # Check ReportLab
    try:
        import reportlab
        dependencies['reportlab'] = True
    except ImportError:
        pass
    
    return dependencies

def get_installation_instructions() -> str:
    """Get platform-specific installation instructions."""
    system = platform.system()
    
    if system == "Windows":
        return """
Windows Installation Instructions:
1. Install Python 3.7+ from https://python.org
2. Install Git from https://git-scm.com
3. Open Command Prompt or PowerShell and run:
   pip install secret-scanner[pdf]
4. For PDF support, you may need to install additional dependencies:
   pip install weasyprint
   # Or use the alternative:
   pip install reportlab
"""
    elif system == "Darwin":  # macOS
        return """
macOS Installation Instructions:
1. Install Python 3.7+ (recommended: use Homebrew)
   brew install python3
2. Install Git (usually pre-installed, or use Homebrew)
   brew install git
3. Install the scanner:
   pip3 install secret-scanner[pdf]
4. For PDF support with WeasyPrint, you may need:
   brew install cairo pango gdk-pixbuf libffi
   pip3 install weasyprint
"""
    else:  # Linux
        return """
Linux Installation Instructions:
1. Install Python 3.7+ and pip:
   sudo apt-get install python3 python3-pip  # Ubuntu/Debian
   sudo yum install python3 python3-pip      # CentOS/RHEL
2. Install Git:
   sudo apt-get install git  # Ubuntu/Debian
   sudo yum install git      # CentOS/RHEL
3. Install the scanner:
   pip3 install secret-scanner[pdf]
4. For PDF support with WeasyPrint, you may need:
   sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
   pip3 install weasyprint
""" 

def validate_platform_compatibility() -> dict:
    """Validate platform compatibility and return detailed status."""
    system = platform.system()
    validation_results = {
        'platform': system,
        'python_version': platform.python_version(),
        'compatible': True,
        'warnings': [],
        'errors': [],
        'recommendations': []
    }
    # Check Python version
    python_version = tuple(map(int, platform.python_version().split('.')))
    if python_version < (3, 7):
        validation_results['compatible'] = False
        validation_results['errors'].append(f"Python {platform.python_version()} is not supported. Python 3.7+ required.")
    # Platform-specific checks
    if system == "Windows":
        try:
            import winreg
            validation_results['windows_features'] = {'registry_access': True}
        except ImportError:
            validation_results['warnings'].append("Windows registry access not available")
        if 'PROGRAMFILES' not in os.environ:
            validation_results['warnings'].append("PROGRAMFILES environment variable not set")
    elif system == "Darwin":  # macOS
        try:
            subprocess.run(['brew', '--version'], capture_output=True, timeout=5)
            validation_results['macos_features'] = {'homebrew_available': True}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            validation_results['recommendations'].append("Consider installing Homebrew for easier dependency management")
    else:  # Linux
        try:
            subprocess.run(['which', 'apt-get'], capture_output=True, timeout=5)
            validation_results['linux_features'] = {'apt_available': True}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            try:
                subprocess.run(['which', 'yum'], capture_output=True, timeout=5)
                validation_results['linux_features'] = {'yum_available': True}
            except (subprocess.TimeoutExpired, FileNotFoundError):
                validation_results['warnings'].append("No supported package manager (apt-get/yum) found")
    try:
        subprocess.run(['git', '--version'], capture_output=True, timeout=5)
        validation_results['git_available'] = True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        validation_results['errors'].append("Git is not available")
        validation_results['compatible'] = False
    return validation_results

def get_platform_specific_commands() -> dict:
    """Get platform-specific commands for common operations."""
    system = platform.system()
    if system == "Windows":
        return {
            'python_cmd': 'python',
            'pip_cmd': 'pip',
            'git_cmd': 'git',
            'package_manager': 'pip',
            'install_cmd': 'pip install',
            'uninstall_cmd': 'pip uninstall',
            'list_cmd': 'pip list',
            'upgrade_cmd': 'pip install --upgrade'
        }
    else:  # Unix-like systems
        return {
            'python_cmd': 'python3',
            'pip_cmd': 'pip3',
            'git_cmd': 'git',
            'package_manager': 'pip3',
            'install_cmd': 'pip3 install',
            'uninstall_cmd': 'pip3 uninstall',
            'list_cmd': 'pip3 list',
            'upgrade_cmd': 'pip3 install --upgrade'
        } 
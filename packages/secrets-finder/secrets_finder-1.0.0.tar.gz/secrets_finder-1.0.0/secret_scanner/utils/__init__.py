"""
Utility modules for theSecrect & PII Scanner.
"""

from .git_utils import GitUtils
from .report_generator import ReportGenerator
from .pre_commit import PreCommitHook
from .multi_project_scanner import MultiProjectScanner
from .email_notifier import EmailNotifier
from .platform_utils import (
    get_system_info,
    is_windows,
    is_macos,
    is_linux,
    get_python_command,
    get_git_command,
    normalize_path,
    get_home_directory,
    get_temp_directory,
    make_executable,
    run_command_safely,
    get_file_encoding,
    safe_read_file,
    get_platform_specific_paths,
    check_dependencies,
    get_installation_instructions
)

__all__ = [
    "GitUtils",
    "ReportGenerator", 
    "PreCommitHook",
    "MultiProjectScanner",
    "EmailNotifier",
    "get_system_info",
    "is_windows",
    "is_macos", 
    "is_linux",
    "get_python_command",
    "get_git_command",
    "normalize_path",
    "get_home_directory",
    "get_temp_directory",
    "make_executable",
    "run_command_safely",
    "get_file_encoding",
    "safe_read_file",
    "get_platform_specific_paths",
    "check_dependencies",
    "get_installation_instructions"
] 
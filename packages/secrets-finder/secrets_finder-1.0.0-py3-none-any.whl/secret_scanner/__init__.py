"""
🔐Secret & PII Scanner

A lightweight, extensible tool to automatically scan source code for hardcoded secrets 
and personally identifiable information (PII) at commit time or during CI/CD pipeline execution.

Features:
- Multi-threaded scanning for performance
- Git integration with diff-based scanning
- Pre-commit hook support
- Multiple output formats (console, JSON, HTML, PDF)
- Customizable detection patterns
- Email notifications
- Multi-project scanning
"""

import os

def get_version():
    """Get version from VERSION file"""
    try:
        version_file = os.path.join(os.path.dirname(__file__), '..', 'VERSION')
        with open(version_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "1.0.0"

__version__ = get_version()
__author__ = "Saravanan Sathiyamoorthi"
__email__ = "saravanansaro976@gmail.com"
__description__ = "A lightweight, extensible tool to automatically scan source code for hardcoded secrets and PII"

# Import main function for console script entry point
from .cli import app as main

# Export main classes for programmatic use
from .core.scanner import SecretScanner
from .core.config import Config
from .core.detectors import BaseDetector, RegexDetector, CustomDetector, DetectorRegistry, Finding
from .utils.git_utils import GitUtils
from .utils.report_generator import ReportGenerator
from .utils.pre_commit import PreCommitHook
from .utils.multi_project_scanner import MultiProjectScanner

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "main",
    "SecretScanner",
    "Config",
    "BaseDetector",
    "RegexDetector", 
    "CustomDetector",
    "DetectorRegistry",
    "Finding",
    "GitUtils",
    "ReportGenerator",
    "PreCommitHook",
    "MultiProjectScanner",
] 
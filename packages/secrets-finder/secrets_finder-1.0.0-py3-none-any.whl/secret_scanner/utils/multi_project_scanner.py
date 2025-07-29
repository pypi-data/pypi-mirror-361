"""
Multi-project scanner for scanning multiple projects in a parent directory.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from ..core.config import Config
from ..utils.report_generator import ReportGenerator
from ..utils.email_notifier import EmailNotifier

class MultiProjectScanner:
    """Scanner for multiple projects in a parent directory."""
    
    def __init__(self, 
                 parent_directory: Path,
                 email_config: Optional[Dict[str, Any]] = None,
                 scanner_config: Optional[Config] = None):
        """
        Initialize multi-project scanner.
        
        Args:
            parent_directory: Path to parent directory containing projects
            email_config: Email configuration for notifications
            scanner_config: Scanner configuration
        """
        self.parent_directory = Path(parent_directory).resolve()
        self.email_config = email_config
        self.scanner_config = scanner_config or Config.load_default()
        self.report_generator = ReportGenerator()
        self.email_notifier = None
        
        if email_config:
            try:
                self.email_notifier = EmailNotifier(email_config)
            except Exception as e:
                print(f"Warning: Email notification disabled - {e}")
        
        self._lock = threading.Lock()
        self.results = {}
    
    def discover_projects(self, 
                         project_patterns: Optional[List[str]] = None,
                         exclude_patterns: Optional[List[str]] = None) -> List[Path]:
        """
        Discover projects in the parent directory.
        
        Args:
            project_patterns: Patterns to identify projects (e.g., ['*', 'project-*'])
            exclude_patterns: Patterns to exclude from scanning
            
        Returns:
            List of project directories
        """
        projects = []
        
        if not self.parent_directory.exists():
            raise ValueError(f"Parent directory does not exist: {self.parent_directory}")
        
        # Default patterns if none provided
        if project_patterns is None:
            project_patterns = ['*']
        
        if exclude_patterns is None:
            exclude_patterns = ['.git', 'node_modules', '__pycache__', '.venv', 'venv', 'env']
        
        # Discover projects
        for pattern in project_patterns:
            for project_path in self.parent_directory.glob(pattern):
                if not project_path.is_dir():
                    continue
                
                # Check if should be excluded
                should_exclude = False
                for exclude_pattern in exclude_patterns:
                    if exclude_pattern in project_path.name or exclude_pattern in str(project_path):
                        should_exclude = True
                        break
                
                if should_exclude:
                    continue
                
                # Check if it looks like a project (has common project files)
                if self._is_project_directory(project_path):
                    projects.append(project_path)
        
        return sorted(projects)
    
    def _is_project_directory(self, directory: Path) -> bool:
        """Check if a directory looks like a project."""
        project_indicators = [
            '.git', 'package.json', 'requirements.txt', 'setup.py', 'pom.xml',
            'build.gradle', 'Cargo.toml', 'go.mod', 'composer.json', 'Gemfile',
            'Dockerfile', 'docker-compose.yml', 'Makefile', 'README.md'
        ]
        
        for indicator in project_indicators:
            if (directory / indicator).exists():
                return True
        
        # Check for source code directories
        source_dirs = ['src', 'lib', 'app', 'main', 'source', 'code']
        for source_dir in source_dirs:
            if (directory / source_dir).exists():
                return True
        
        return False
    
    def scan_project(self, project_path: Path) -> Dict[str, Any]:
        """
        Scan a single project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary containing scan results
        """
        from ..core.scanner import SecretScanner  # Moved import here to avoid circular import
        try:
            # Initialize scanner for this project
            scanner = SecretScanner(self.scanner_config)
            
            # Get files to scan
            files_to_scan = scanner.get_files_to_scan(project_path)
            
            if not files_to_scan:
                return {
                    'project_name': project_path.name,
                    'project_path': str(project_path),
                    'status': 'no_files',
                    'findings': [],
                    'summary': {
                        'total_findings': 0,
                        'by_severity': {},
                        'by_category': {},
                        'files_affected': []
                    },
                    'error': None
                }
            
            # Perform scan
            findings = scanner.scan_files(files_to_scan)
            summary = scanner.get_findings_summary(findings)
            
            return {
                'project_name': project_path.name,
                'project_path': str(project_path),
                'status': 'completed',
                'findings': findings,
                'summary': summary,
                'error': None
            }
            
        except Exception as e:
            return {
                'project_name': project_path.name,
                'project_path': str(project_path),
                'status': 'error',
                'findings': [],
                'summary': {
                    'total_findings': 0,
                    'by_severity': {},
                    'by_category': {},
                    'files_affected': []
                },
                'error': str(e)
            }
    
    def scan_all_projects(self, 
                         project_patterns: Optional[List[str]] = None,
                         exclude_patterns: Optional[List[str]] = None,
                         max_workers: Optional[int] = None,
                         progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Scan all projects in the parent directory.
        
        Args:
            project_patterns: Patterns to identify projects
            exclude_patterns: Patterns to exclude from scanning
            max_workers: Maximum number of worker threads
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing results for all projects
        """
        # Discover projects
        projects = self.discover_projects(project_patterns, exclude_patterns)
        
        if not projects:
            return {
                'scan_date': datetime.now().isoformat(),
                'parent_directory': str(self.parent_directory),
                'projects_found': 0,
                'projects_scanned': 0,
                'total_findings': 0,
                'projects': [],
                'overall_summary': {
                    'total_findings': 0,
                    'by_severity': {},
                    'by_category': {},
                    'files_affected': []
                }
            }
        
        if progress_callback:
            progress_callback(f"Found {len(projects)} projects to scan", 0, len(projects))
        
        # Determine number of workers
        if max_workers is None:
            max_workers = min(len(projects), self.scanner_config.max_workers)
        
        # Scan projects
        results = {
            'scan_date': datetime.now().isoformat(),
            'parent_directory': str(self.parent_directory),
            'projects_found': len(projects),
            'projects_scanned': 0,
            'total_findings': 0,
            'projects': [],
            'overall_summary': {
                'total_findings': 0,
                'by_severity': {},
                'by_category': {},
                'files_affected': set()
            }
        }
        
        # Use multi-threading for project scanning
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_project = {
                executor.submit(self.scan_project, project_path): project_path 
                for project_path in projects
            }
            
            for future in as_completed(future_to_project):
                project_path = future_to_project[future]
                try:
                    project_result = future.result()
                    results['projects'].append(project_result)
                    results['projects_scanned'] += 1
                    
                    # Update overall summary
                    if project_result['status'] == 'completed':
                        results['total_findings'] += project_result['summary']['total_findings']
                        
                        # Aggregate severity counts
                        for severity, count in project_result['summary']['by_severity'].items():
                            results['overall_summary']['by_severity'][severity] = \
                                results['overall_summary']['by_severity'].get(severity, 0) + count
                        
                        # Aggregate category counts
                        for category, count in project_result['summary']['by_category'].items():
                            results['overall_summary']['by_category'][category] = \
                                results['overall_summary']['by_category'].get(category, 0) + count
                        
                        # Aggregate affected files
                        for file_path in project_result['summary']['files_affected']:
                            results['overall_summary']['files_affected'].add(file_path)
                    
                    if progress_callback:
                        progress_callback(
                            f"Scanned {project_result['project_name']} ({project_result['summary']['total_findings']} findings)",
                            results['projects_scanned'],
                            len(projects)
                        )
                    
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"Error scanning {project_path.name}: {e}", results['projects_scanned'], len(projects))
        
        # Convert set to list for JSON serialization
        results['overall_summary']['files_affected'] = list(results['overall_summary']['files_affected'])
        results['overall_summary']['total_findings'] = results['total_findings']
        
        return results
    
    def generate_reports(self, 
                        results: Dict[str, Any], 
                        output_dir: Optional[Path] = None,
                        report_path: Optional[str] = None,
                        report_name: Optional[str] = None) -> Dict[str, Path]:
        """
        Generate summary reports for multi-project scan.
        Args:
            results: Scan results
            output_dir: Directory to save reports
            report_path: Full path for the summary report (overrides report_name)
            report_name: Custom summary report filename (used in output_dir or current dir)
        Returns:
            Dict of report type to file path
        """
        report_paths = {}
        # Determine base path for summary report
        if report_path:
            base_path = Path(report_path)
        else:
            if report_name:
                base_path = Path(report_name)
                if not base_path.is_absolute():
                    base_path = (Path(output_dir) if output_dir else Path.cwd()) / base_path
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_path = (Path(output_dir) if output_dir else Path.cwd()) / f"multi_project_scan_report_{timestamp}"
        # Save HTML summary
        html_path = base_path.with_suffix('.html')
        self.report_generator.save_multi_project_html_report(results, html_path)
        report_paths['html'] = html_path
        # Save PDF summary
        try:
            pdf_path = base_path.with_suffix('.pdf')
            self.report_generator.save_multi_project_pdf_report(results, pdf_path)
            report_paths['pdf'] = pdf_path
        except Exception as e:
            pass
        return report_paths
    
    def send_email_notification(self, 
                               results: Dict[str, Any], 
                               report_paths: Dict[str, Path],
                               project_name: str = None) -> bool:
        """
        Send hybrid email notification with main report and individual project reports.
        
        Args:
            results: Scan results
            report_paths: Dictionary containing report file paths
            project_name: Name for the email subject
            
        Returns:
            bool: True if email sent successfully
        """
        if not self.email_notifier:
            print("Email notification not configured")
            return False
        
        if project_name is None:
            project_name = f"Multi-Project Scan - {self.parent_directory.name}"
        
        # Use the new hybrid email method
        main_pdf_path = report_paths.get('pdf')
        project_pdfs = report_paths.get('project_pdfs', {})
        
        if main_pdf_path and main_pdf_path.exists():
            return self.email_notifier.send_multi_project_email(
                main_pdf_path=main_pdf_path,
                project_pdfs=project_pdfs,
                scan_results=results,
                parent_directory_name=self.parent_directory.name
            )
        else:
            print("Main PDF report not found")
            return False
    
    def run_automated_scan(self,
                          project_patterns: Optional[List[str]] = None,
                          exclude_patterns: Optional[List[str]] = None,
                          max_workers: Optional[int] = None,
                          output_dir: Optional[Path] = None,
                          send_email: bool = True,
                          progress_callback: Optional[Callable] = None,
                          report_path: Optional[str] = None,
                          report_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Run complete automated scan with reporting and notification.
        
        Args:
            project_patterns: Patterns to identify projects
            exclude_patterns: Patterns to exclude from scanning
            max_workers: Maximum number of worker threads
            output_dir: Directory to save reports
            send_email: Whether to send email notification
            progress_callback: Optional callback for progress updates
            report_path: Full path for the summary report (overrides report_name)
            report_name: Custom summary report filename (used in output_dir or current dir)
            
        Returns:
            Dictionary containing scan results and report paths
        """
        if progress_callback:
            progress_callback(f"Starting automated scan of {self.parent_directory}", 0, 3)
        
        # Scan all projects
        results = self.scan_all_projects(project_patterns, exclude_patterns, max_workers, progress_callback)
        
        if progress_callback:
            progress_callback("Generating reports...", 1, 3)
        
        # Generate reports
        report_paths = self.generate_reports(results, output_dir, report_path, report_name)
        
        if progress_callback:
            progress_callback("Sending email notification...", 2, 3)
        
        # Send email notification if configured
        email_sent = False
        if send_email and self.email_notifier and 'pdf' in report_paths:
            email_sent = self.send_email_notification(results, report_paths)
        
        if progress_callback:
            progress_callback("Scan completed!", 3, 3)
        
        return {
            'results': results,
            'report_paths': report_paths,
            'email_sent': email_sent
        } 
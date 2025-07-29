"""
Main scanner class for detecting secrets and PII in source code.
"""

import fnmatch
from pathlib import Path
from typing import List, Optional, Set, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from .config import ScannerConfig
from .detectors import DetectorRegistry, Finding, RegexDetector
from ..utils.platform_utils import safe_read_file

class SecretScanner:
    """Main scanner class for detecting secrets and PII."""
    
    def __init__(self, config: ScannerConfig):
        self.config = config
        self.detector_registry = DetectorRegistry()
        self._setup_detectors()
        self._lock = threading.Lock()  # For thread-safe operations
    
    def _setup_detectors(self):
        """Setup all detectors based on configuration."""
        # Add regex-based detectors from config
        for pattern in self.config.patterns:
            detector = RegexDetector(
                name=pattern.name,
                regex=pattern.regex,
                severity=pattern.severity,
                category=pattern.category,
                description=pattern.description
            )
            self.detector_registry.add_detector(detector)
    
    def get_files_to_scan(self, root_path: Path, file_patterns: Optional[List[str]] = None) -> List[Path]:
        """Get list of files to scan based on configuration and patterns."""
        files_to_scan = []
        total_files_found = 0
        
        if root_path.is_file():
            total_files_found = 1
            if self._should_scan_file(root_path, file_patterns):
                files_to_scan.append(root_path)
            return files_to_scan
        
        # Walk through directory
        for file_path in root_path.rglob('*'):
            if file_path.is_file():
                total_files_found += 1
                if self._should_scan_file(file_path, file_patterns):
                    files_to_scan.append(file_path)
        
        # Log scanning statistics
        if hasattr(self.config, 'show_skipped_files') and self.config.show_skipped_files:
            skipped_count = total_files_found - len(files_to_scan)
            print(f"📊 File scanning stats: {total_files_found} total files found, {len(files_to_scan)} files to scan, {skipped_count} files skipped")
        
        return files_to_scan
    
    def _should_scan_file(self, file_path: Path, file_patterns: Optional[List[str]] = None) -> bool:
        """Determine if a file should be scanned based on configuration."""
        # Check file size
        try:
            if file_path.stat().st_size > self.config.max_file_size:
                if hasattr(self.config, 'show_skipped_files') and self.config.show_skipped_files:
                    print(f"⏭️  Skipping {file_path} (too large: {file_path.stat().st_size / (1024*1024):.1f}MB)")
                return False
        except (OSError, IOError):
            if hasattr(self.config, 'show_skipped_files') and self.config.show_skipped_files:
                print(f"⏭️  Skipping {file_path} (cannot read file)")
            return False
        
        # Check exclude patterns
        for exclude_pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(str(file_path), exclude_pattern):
                if hasattr(self.config, 'show_skipped_files') and self.config.show_skipped_files:
                    print(f"⏭️  Skipping {file_path} (exclude pattern: {exclude_pattern})")
                return False
            if fnmatch.fnmatch(file_path.name, exclude_pattern):
                if hasattr(self.config, 'show_skipped_files') and self.config.show_skipped_files:
                    print(f"⏭️  Skipping {file_path} (exclude pattern: {exclude_pattern})")
                return False
        
        # Check include patterns
        if self.config.include_patterns:
            should_include = False
            for include_pattern in self.config.include_patterns:
                if fnmatch.fnmatch(str(file_path), include_pattern):
                    should_include = True
                    break
                if fnmatch.fnmatch(file_path.name, include_pattern):
                    should_include = True
                    break
            if not should_include:
                if hasattr(self.config, 'show_skipped_files') and self.config.show_skipped_files:
                    print(f"⏭️  Skipping {file_path} (not in include patterns)")
                return False
        
        # Check custom file patterns
        if file_patterns:
            should_include = False
            for pattern in file_patterns:
                if fnmatch.fnmatch(str(file_path), pattern):
                    should_include = True
                    break
                if fnmatch.fnmatch(file_path.name, pattern):
                    should_include = True
                    break
            if not should_include:
                if hasattr(self.config, 'show_skipped_files') and self.config.show_skipped_files:
                    print(f"⏭️  Skipping {file_path} (not in file patterns)")
                return False
        
        return True
    
    def scan_file(self, file_path: Path) -> List[Finding]:
        """Scan a single file for secrets and PII."""
        try:
            # Read file content using platform-safe method
            content = safe_read_file(file_path, max_size=self.config.max_file_size)
            
            if content is None:
                # File couldn't be read (too large, binary, or permission issues)
                return []
            
            # Run all detectors
            findings = self.detector_registry.detect_all(content, file_path)
            
            return findings
        
        except Exception as e:
            # Log error and continue
            print(f"Error scanning file {file_path}: {e}")
            return []
    
    def _scan_file_worker(self, file_path: Path, progress_callback: Optional[Callable] = None) -> tuple[Path, List[Finding]]:
        """Worker function for scanning a single file in a thread."""
        findings = self.scan_file(file_path)
        if progress_callback:
            progress_callback(file_path, len(findings))
        return file_path, findings
    
    def scan_files(self, file_paths: List[Path], progress_callback: Optional[Callable] = None) -> List[Finding]:
        """Scan multiple files for secrets and PII using multi-threading."""
        all_findings = []
        total_files = len(file_paths)
        
        if progress_callback:
            progress_callback(None, 0, total_files)  # Initialize progress
        
        # Use single-threaded scanning for small file sets
        if len(file_paths) <= self.config.chunk_size:
            for i, file_path in enumerate(file_paths):
                findings = self.scan_file(file_path)
                all_findings.extend(findings)
                if progress_callback:
                    progress_callback(file_path, len(findings), total_files, i + 1)
            return all_findings
        
        # Use multi-threaded scanning for larger file sets
        completed_files = 0
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all file scanning tasks
            future_to_file = {
                executor.submit(self._scan_file_worker, file_path, None): file_path 
                for file_path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_path, findings = future.result()
                    with self._lock:
                        all_findings.extend(findings)
                        completed_files += 1
                        if progress_callback:
                            progress_callback(file_path, len(findings), total_files, completed_files)
                except Exception as e:
                    print(f"Error scanning file {file_path}: {e}")
                    completed_files += 1
                    if progress_callback:
                        progress_callback(file_path, 0, total_files, completed_files)
        
        return all_findings
    
    def scan_directory(self, directory_path: Path, file_patterns: Optional[List[str]] = None, progress_callback: Optional[Callable] = None) -> List[Finding]:
        """Scan a directory for secrets and PII."""
        files_to_scan = self.get_files_to_scan(directory_path, file_patterns)
        return self.scan_files(files_to_scan, progress_callback)
    
    def add_custom_detector(self, detector):
        """Add a custom detector to the scanner."""
        with self._lock:
            self.detector_registry.add_detector(detector)
    
    def remove_detector(self, detector_name: str) -> bool:
        """Remove a detector by name."""
        with self._lock:
            return self.detector_registry.remove_detector(detector_name)
    
    def get_detector_names(self) -> List[str]:
        """Get list of all detector names."""
        with self._lock:
            return [detector.name for detector in self.detector_registry.detectors]
    
    def get_findings_summary(self, findings: List[Finding]) -> dict:
        """Get a summary of findings."""
        summary = {
            'total_findings': len(findings),
            'by_severity': {},
            'by_category': {},
            'by_pattern': {},
            'files_affected': set()
        }
        
        for finding in findings:
            # Count by severity
            severity = finding.severity
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Count by category
            category = finding.category
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
            
            # Count by pattern
            pattern = finding.pattern_name
            summary['by_pattern'][pattern] = summary['by_pattern'].get(pattern, 0) + 1
            
            # Track affected files
            summary['files_affected'].add(str(finding.file_path))
        
        # Convert set to list for JSON serialization
        summary['files_affected'] = list(summary['files_affected'])
        
        return summary 
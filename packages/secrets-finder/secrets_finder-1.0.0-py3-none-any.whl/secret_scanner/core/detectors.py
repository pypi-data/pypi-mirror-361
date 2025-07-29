"""
Detection engines for secrets and PII.
"""

import re
import math
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Finding:
    """Represents a detected secret or PII finding."""
    file_path: Path
    line_number: int
    column: int
    pattern_name: str
    severity: str
    matched_text: str
    context: str
    category: str
    description: Optional[str] = None
    entropy_score: Optional[float] = None

class BaseDetector(ABC):
    """Base class for all detectors."""
    
    def __init__(self, name: str, severity: str = "medium", category: str = "secret"):
        self.name = name
        self.severity = severity
        self.category = category
    
    @abstractmethod
    def detect(self, content: str, file_path: Path) -> List[Finding]:
        """Detect secrets/PII in the given content."""
        pass

class RegexDetector(BaseDetector):
    """Regex-based detector for secrets and PII."""
    
    def __init__(self, name: str, regex: str, severity: str = "medium", 
                 category: str = "secret", description: Optional[str] = None):
        super().__init__(name, severity, category)
        self.regex = regex
        self.description = description
        self.compiled_regex = re.compile(regex, re.IGNORECASE | re.MULTILINE)
    
    def detect(self, content: str, file_path: Path) -> List[Finding]:
        """Detect secrets using regex pattern."""
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            matches = self.compiled_regex.finditer(line)
            for match in matches:
                # Get context around the match
                start_line = max(1, line_num - 2)
                end_line = min(len(lines), line_num + 2)
                context_lines = lines[start_line-1:end_line]
                context = '\n'.join(context_lines)
                
                finding = Finding(
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start() + 1,
                    pattern_name=self.name,
                    severity=self.severity,
                    matched_text=match.group(),
                    context=context,
                    category=self.category,
                    description=self.description
                )
                findings.append(finding)
        
        return findings

class CustomDetector(BaseDetector):
    """Custom detector that can be extended with user-defined logic."""
    
    def __init__(self, name: str, detection_func, severity: str = "medium", 
                 category: str = "custom", description: Optional[str] = None):
        super().__init__(name, severity, category)
        self.detection_func = detection_func
        self.description = description
    
    def detect(self, content: str, file_path: Path) -> List[Finding]:
        """Use custom detection function."""
        try:
            return self.detection_func(content, file_path, self)
        except Exception as e:
            # Log error and return empty findings
            print(f"Error in custom detector '{self.name}': {e}")
            return []

class DetectorRegistry:
    """Registry for managing all detectors."""
    
    def __init__(self):
        self.detectors: List[BaseDetector] = []
    
    def add_detector(self, detector: BaseDetector):
        """Add a detector to the registry."""
        self.detectors.append(detector)
    
    def add_regex_detector(self, name: str, regex: str, severity: str = "medium", 
                          category: str = "secret", description: Optional[str] = None):
        """Add a regex-based detector."""
        detector = RegexDetector(name, regex, severity, category, description)
        self.add_detector(detector)
    
    def add_custom_detector(self, name: str, detection_func, severity: str = "medium", 
                            category: str = "custom", description: Optional[str] = None):
        """Add a custom detector."""
        detector = CustomDetector(name, detection_func, severity, category, description)
        self.add_detector(detector)
    
    def detect_all(self, content: str, file_path: Path) -> List[Finding]:
        """Run all detectors on the content."""
        all_findings = []
        
        for detector in self.detectors:
            try:
                findings = detector.detect(content, file_path)
                all_findings.extend(findings)
            except Exception as e:
                print(f"Error in detector '{detector.name}': {e}")
                continue
        
        return all_findings
    
    def get_detector_by_name(self, name: str) -> Optional[BaseDetector]:
        """Get detector by name."""
        for detector in self.detectors:
            if detector.name == name:
                return detector
        return None
    
    def remove_detector(self, name: str) -> bool:
        """Remove detector by name."""
        for i, detector in enumerate(self.detectors):
            if detector.name == name:
                del self.detectors[i]
                return True
        return False 
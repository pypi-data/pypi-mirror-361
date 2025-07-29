"""
Report generator for Secret scanner findings.
"""

import json
import datetime
import platform
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from jinja2 import Template

# Try to import XML libraries
try:
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    XML_AVAILABLE = True
except ImportError:
    XML_AVAILABLE = False

# Try to import defusedxml for secure XML parsing
try:
    from defusedxml import ElementTree as SafeET
    from defusedxml import minidom as SafeMinidom
    SAFE_XML_AVAILABLE = True
except ImportError:
    SAFE_XML_AVAILABLE = False

# Try to import WeasyPrint, but provide fallback if not available
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    weasyprint = None

# Try to import ReportLab as fallback
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table as RLTable, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..core.detectors import Finding

console = Console()

class ReportGenerator:
    """Generate reports in various formats."""
    
    def __init__(self):
        self.html_template = self._get_html_template()
    
    def print_console_report(self, findings: List[Finding], verbose: bool = False):
        """Print findings to console with rich formatting."""
        if not findings:
            console.print("[green]✅ No secrets or PII found![/green]")
            return
        
        # Summary
        summary = self._get_summary(findings)
        self._print_summary(summary)
        
        # Group findings by file
        findings_by_file = {}
        for finding in findings:
            file_path = str(finding.file_path)
            if file_path not in findings_by_file:
                findings_by_file[file_path] = []
            findings_by_file[file_path].append(finding)
        
        # Print findings by file
        for file_path, file_findings in findings_by_file.items():
            console.print(f"\n[bold blue]📁 {file_path}[/bold blue]")
            
            for finding in file_findings:
                self._print_finding(finding, verbose)
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print summary statistics."""
        console.print("\n[bold]📊 Scan Summary[/bold]")
        
        # Create summary table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")
        
        table.add_row("Total Findings", str(summary['total_findings']))
        table.add_row("Files Affected", str(len(summary['files_affected'])))
        
        # Severity breakdown
        for severity, count in summary['by_severity'].items():
            severity_color = self._get_severity_color(severity)
            table.add_row(f"  {severity.title()}", f"[{severity_color}]{count}[/{severity_color}]")
        
        # Category breakdown
        for category, count in summary['by_category'].items():
            table.add_row(f"  {category.title()}", str(count))
        
        console.print(table)
    
    def _print_finding(self, finding: Finding, verbose: bool):
        """Print a single finding."""
        severity_color = self._get_severity_color(finding.severity)
        severity_icon = self._get_severity_icon(finding.severity)
        
        # Main finding info
        console.print(f"\n  {severity_icon} [bold {severity_color}]{finding.pattern_name}[/]")
        console.print(f"    📍 Line {finding.line_number}, Column {finding.column}")
        console.print(f"    🏷️  {finding.category.title()} - {finding.severity.title()}")
        
        if finding.description:
            console.print(f"    📝 {finding.description}")
        
        # Show matched text (truncated if too long)
        matched_text = finding.matched_text
        if len(matched_text) > 100:
            matched_text = matched_text[:97] + "..."
        
        console.print(f"    🔍 [red]{matched_text}[/red]")
        
        if verbose:
            # Show context
            console.print("    📄 Context:")
            context_lines = finding.context.split('\n')
            for i, line in enumerate(context_lines):
                line_num = finding.line_number - 2 + i
                if line_num == finding.line_number:
                    console.print(f"    [bold red]>> {line_num:4d}: {line}[/bold red]")
                else:
                    console.print(f"    {line_num:4d}: {line}")
        
        if finding.entropy_score:
            console.print(f"    🎲 Entropy Score: {finding.entropy_score:.2f}")
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level."""
        colors = {
            'low': 'yellow',
            'medium': 'orange',
            'high': 'red',
            'critical': 'bold red'
        }
        return colors.get(severity, 'white')
    
    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for severity level."""
        icons = {
            'low': '🔶',
            'medium': '🔸',
            'high': '🔴',
            'critical': '💀'
        }
        return icons.get(severity, '❓')
    
    def _get_summary(self, findings: List[Finding]) -> Dict[str, Any]:
        """Get summary statistics for findings."""
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
    
    def save_json_report(self, findings: List[Finding], output_path: str):
        """Save findings as JSON report."""
        report_data = {
            'scan_summary': self._get_summary(findings),
            'scan_timestamp': datetime.datetime.now().isoformat(),
            'findings': []
        }
        
        for finding in findings:
            finding_data = {
                'file': str(finding.file_path),
                'line': finding.line_number,
                'column': finding.column,
                'pattern': finding.pattern_name,
                'severity': finding.severity,
                'category': finding.category,
                'matched_text': finding.matched_text,
                'context': finding.context,
                'description': finding.description,
                'entropy_score': finding.entropy_score
            }
            report_data['findings'].append(finding_data)
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
    
    def save_html_report(self, findings: List[Finding], output_path: str):
        """Save findings as HTML report."""
        report_data = {
            'scan_summary': self._get_summary(findings),
            'scan_timestamp': datetime.datetime.now().isoformat(),
            'findings': findings
        }
        
        html_content = self.html_template.render(**report_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def save_pdf_report(self, findings: List[Finding], output_path: str):
        """Save findings as PDF report."""
        if WEASYPRINT_AVAILABLE:
            self._save_pdf_with_weasyprint(findings, output_path)
        elif REPORTLAB_AVAILABLE:
            self._save_pdf_with_reportlab(findings, output_path)
        else:
            raise ImportError(
                "PDF generation requires either WeasyPrint or ReportLab. "
                "Install with: pip install weasyprint or pip install reportlab"
            )
    
    def _save_pdf_with_weasyprint(self, findings: List[Finding], output_path: str):
        """Save PDF using WeasyPrint."""
        report_data = {
            'scan_summary': self._get_summary(findings),
            'scan_timestamp': datetime.datetime.now().isoformat(),
            'findings': findings
        }
        
        html_content = self.html_template.render(**report_data)
        
        # Convert HTML to PDF
        weasyprint.HTML(string=html_content).write_pdf(output_path)
    
    def _save_pdf_with_reportlab(self, findings: List[Finding], output_path: str):
        """Save PDF using ReportLab as fallback."""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph("🔐Secret & PII Scanner Report", title_style))
        story.append(Spacer(1, 20))
        
        # Summary
        summary = self._get_summary(findings)
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20
        )
        
        story.append(Paragraph(f"<b>Scan Summary:</b>", summary_style))
        story.append(Paragraph(f"Total Findings: {summary['total_findings']}", summary_style))
        story.append(Paragraph(f"Files Affected: {len(summary['files_affected'])}", summary_style))
        story.append(Spacer(1, 20))
        
        # Severity breakdown
        story.append(Paragraph("<b>Severity Breakdown:</b>", summary_style))
        for severity, count in summary['by_severity'].items():
            story.append(Paragraph(f"  {severity.title()}: {count}", summary_style))
        story.append(Spacer(1, 20))
        
        # Findings
        if findings:
            story.append(Paragraph("<b>Findings:</b>", summary_style))
            
            for finding in findings:
                # Finding header
                finding_style = ParagraphStyle(
                    'Finding',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=10,
                    leftIndent=20
                )
                
                story.append(Paragraph(
                    f"<b>{finding.pattern_name}</b> ({finding.severity.upper()}) - {finding.file_path.name}:{finding.line_number}",
                    finding_style
                ))
                
                # Finding details
                detail_style = ParagraphStyle(
                    'Detail',
                    parent=styles['Normal'],
                    fontSize=10,
                    spaceAfter=5,
                    leftIndent=40
                )
                
                story.append(Paragraph(f"Category: {finding.category}", detail_style))
                story.append(Paragraph(f"Matched: {finding.matched_text[:100]}{'...' if len(finding.matched_text) > 100 else ''}", detail_style))
                
                if finding.description:
                    story.append(Paragraph(f"Description: {finding.description}", detail_style))
                
                story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
    
    def save_csv_report(self, findings: List[Finding], output_path: str):
        """Save findings as CSV report."""
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'file', 'line', 'column', 'pattern', 'severity', 'category',
                'matched_text', 'description', 'entropy_score', 'context'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for finding in findings:
                writer.writerow({
                    'file': str(finding.file_path),
                    'line': finding.line_number,
                    'column': finding.column,
                    'pattern': finding.pattern_name,
                    'severity': finding.severity,
                    'category': finding.category,
                    'matched_text': finding.matched_text,
                    'description': finding.description or '',
                    'entropy_score': finding.entropy_score or '',
                    'context': finding.context.replace('\n', '\\n')
                })
    
    def save_xml_report(self, findings: List[Finding], output_path: str):
        """Save findings as XML report."""
        if not XML_AVAILABLE:
            raise ImportError("XML generation requires xml.etree.ElementTree")
        
        # Create root element
        root = ET.Element("secret_scan_report")
        root.set("timestamp", datetime.datetime.now().isoformat())
        root.set("total_findings", str(len(findings)))
        
        # Add summary
        summary = self._get_summary(findings)
        summary_elem = ET.SubElement(root, "summary")
        ET.SubElement(summary_elem, "total_findings").text = str(summary['total_findings'])
        ET.SubElement(summary_elem, "files_affected").text = str(len(summary['files_affected']))
        
        # Add severity breakdown
        severity_elem = ET.SubElement(summary_elem, "severity_breakdown")
        for severity, count in summary['by_severity'].items():
            sev_elem = ET.SubElement(severity_elem, "severity")
            sev_elem.set("level", severity)
            sev_elem.set("count", str(count))
        
        # Add findings
        findings_elem = ET.SubElement(root, "findings")
        for finding in findings:
            finding_elem = ET.SubElement(findings_elem, "finding")
            finding_elem.set("file", str(finding.file_path))
            finding_elem.set("line", str(finding.line_number))
            finding_elem.set("column", str(finding.column))
            finding_elem.set("pattern", finding.pattern_name)
            finding_elem.set("severity", finding.severity)
            finding_elem.set("category", finding.category)
            
            ET.SubElement(finding_elem, "matched_text").text = finding.matched_text
            if finding.description:
                ET.SubElement(finding_elem, "description").text = finding.description
            if finding.entropy_score:
                ET.SubElement(finding_elem, "entropy_score").text = str(finding.entropy_score)
            ET.SubElement(finding_elem, "context").text = finding.context
        
        # Write XML with pretty formatting
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
    
    def save_sarif_report(self, findings: List[Finding], output_path: str):
        """Save findings as SARIF (Static Analysis Results Interchange Format) report."""
        sarif_report = {
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Secret Scanner",
                            "version": "1.0.0",
                            "informationUri": "https://gitlab.com/ox-saro/SecretDetection"
                        }
                    },
                    "invocations": [
                        {
                            "executionSuccessful": True,
                            "startTimeUtc": datetime.datetime.now().isoformat() + "Z"
                        }
                    ],
                    "results": []
                }
            ]
        }
        
        # Convert findings to SARIF format
        for finding in findings:
            # Map severity levels to SARIF levels
            severity_map = {
                'critical': 'error',
                'high': 'error',
                'medium': 'warning',
                'low': 'note'
            }
            
            sarif_result = {
                "ruleId": finding.pattern_name,
                "level": severity_map.get(finding.severity, 'warning'),
                "message": {
                    "text": f"Potential {finding.category} detected: {finding.matched_text}"
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": str(finding.file_path)
                            },
                            "region": {
                                "startLine": finding.line_number,
                                "startColumn": finding.column,
                                "endLine": finding.line_number,
                                "endColumn": finding.column + len(finding.matched_text)
                            }
                        }
                    }
                ],
                "properties": {
                    "category": finding.category,
                    "severity": finding.severity,
                    "entropy_score": finding.entropy_score
                }
            }
            
            if finding.description:
                sarif_result["message"]["text"] += f" - {finding.description}"
            
            sarif_report["runs"][0]["results"].append(sarif_result)
        
        # Write SARIF report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sarif_report, f, indent=2, ensure_ascii=False)
    
    def save_junit_report(self, findings: List[Finding], output_path: str):
        """Save findings as JUnit XML report for CI/CD integration."""
        if not XML_AVAILABLE:
            raise ImportError("JUnit XML generation requires xml.etree.ElementTree")
        
        # Create root element
        root = ET.Element("testsuites")
        root.set("name", "Secret Scanner")
        root.set("tests", str(len(findings)))
        root.set("failures", str(len(findings)))
        root.set("errors", "0")
        root.set("time", "0")
        
        # Group findings by file
        findings_by_file = {}
        for finding in findings:
            file_path = str(finding.file_path)
            if file_path not in findings_by_file:
                findings_by_file[file_path] = []
            findings_by_file[file_path].append(finding)
        
        # Create testsuite for each file
        for file_path, file_findings in findings_by_file.items():
            testsuite = ET.SubElement(root, "testsuite")
            testsuite.set("name", file_path)
            testsuite.set("tests", str(len(file_findings)))
            testsuite.set("failures", str(len(file_findings)))
            testsuite.set("errors", "0")
            testsuite.set("time", "0")
            
            for finding in file_findings:
                testcase = ET.SubElement(testsuite, "testcase")
                testcase.set("name", f"{finding.pattern_name} at line {finding.line_number}")
                testcase.set("classname", str(finding.file_path))
                testcase.set("time", "0")
                
                failure = ET.SubElement(testcase, "failure")
                failure.set("message", f"{finding.severity.upper()}: {finding.pattern_name}")
                failure.set("type", "SecretDetection")
                
                failure_text = f"""
Severity: {finding.severity.upper()}
Category: {finding.category}
Pattern: {finding.pattern_name}
Line: {finding.line_number}, Column: {finding.column}
Matched Text: {finding.matched_text}
Context: {finding.context}
"""
                if finding.description:
                    failure_text += f"Description: {finding.description}\n"
                if finding.entropy_score:
                    failure_text += f"Entropy Score: {finding.entropy_score}\n"
                
                failure.text = failure_text.strip()
        
        # Write JUnit XML with pretty formatting
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
    
    def export_filtered_findings(self, findings: List[Finding], 
                                severity_filter: Optional[List[str]] = None,
                                category_filter: Optional[List[str]] = None,
                                pattern_filter: Optional[List[str]] = None,
                                file_filter: Optional[List[str]] = None) -> List[Finding]:
        """Export findings filtered by various criteria."""
        filtered_findings = findings.copy()
        
        if severity_filter:
            filtered_findings = [f for f in filtered_findings if f.severity in severity_filter]
        
        if category_filter:
            filtered_findings = [f for f in filtered_findings if f.category in category_filter]
        
        if pattern_filter:
            filtered_findings = [f for f in filtered_findings if f.pattern_name in pattern_filter]
        
        if file_filter:
            filtered_findings = [f for f in filtered_findings if any(
                filter_pattern in str(f.file_path) for filter_pattern in file_filter
            )]
        
        return filtered_findings
    
    def get_report_formats(self) -> Dict[str, str]:
        """Get available report formats with descriptions."""
        return {
            'console': 'Rich console output with colors and formatting',
            'json': 'Structured JSON format for programmatic processing',
            'html': 'Interactive HTML report with modern styling',
            'pdf': 'PDF report (requires WeasyPrint or ReportLab)',
            'csv': 'Comma-separated values for spreadsheet import',
            'xml': 'Structured XML format for enterprise tools',
            'sarif': 'SARIF format for security tool integration',
            'junit': 'JUnit XML format for CI/CD integration'
        }
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform information for cross-platform compatibility."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'available_formats': {
                'pdf': WEASYPRINT_AVAILABLE or REPORTLAB_AVAILABLE,
                'xml': XML_AVAILABLE,
                'safe_xml': SAFE_XML_AVAILABLE
            }
        }
    
    def save_multi_project_pdf_report(self, results: Dict[str, Any], output_path: Path):
        """Save multi-project scan results as PDF report."""
        if WEASYPRINT_AVAILABLE:
            html_content = self._get_multi_project_html_template().render(**results)
            weasyprint.HTML(string=html_content).write_pdf(str(output_path))
        elif REPORTLAB_AVAILABLE:
            self._save_multi_project_pdf_with_reportlab(results, output_path)
        else:
            raise ImportError(
                "PDF generation requires either WeasyPrint or ReportLab. "
                "Install with: pip install weasyprint or pip install reportlab"
            )
    
    def _save_multi_project_pdf_with_reportlab(self, results: Dict[str, Any], output_path: Path):
        """Save multi-project PDF using ReportLab."""
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("🔐 Multi-Project Secret Scanner Report", title_style))
        story.append(Spacer(1, 20))
        
        # Summary
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20
        )
        
        story.append(Paragraph(f"<b>Scan Summary:</b>", summary_style))
        story.append(Paragraph(f"Projects Found: {results.get('projects_found', 0)}", summary_style))
        story.append(Paragraph(f"Projects Scanned: {results.get('projects_scanned', 0)}", summary_style))
        story.append(Paragraph(f"Total Findings: {results.get('total_findings', 0)}", summary_style))
        story.append(Spacer(1, 20))
        
        # Projects
        if 'projects' in results:
            story.append(Paragraph("<b>Project Results:</b>", summary_style))
            
            for project in results['projects']:
                project_style = ParagraphStyle(
                    'Project',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=10,
                    leftIndent=20
                )
                
                story.append(Paragraph(
                    f"<b>{project.get('project_name', 'Unknown')}</b> - {project.get('status', 'Unknown')}",
                    project_style
                ))
                
                detail_style = ParagraphStyle(
                    'Detail',
                    parent=styles['Normal'],
                    fontSize=10,
                    spaceAfter=5,
                    leftIndent=40
                )
                
                story.append(Paragraph(f"Path: {project.get('project_path', 'Unknown')}", detail_style))
                story.append(Paragraph(f"Findings: {project.get('summary', {}).get('total_findings', 0)}", detail_style))
                
                if project.get('error'):
                    story.append(Paragraph(f"Error: {project['error']}", detail_style))
                
                story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
    
    def save_multi_project_html_report(self, results: Dict[str, Any], output_path: Path):
        """Save multi-project scan results as HTML report."""
        html_content = self._get_multi_project_html_template().render(**results)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _get_multi_project_html_template(self) -> Template:
        """Get HTML template for multi-project reports."""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Multi-Project Secret Scanner Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
                .summary-card { background-color: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }
                .severity-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 20px 0; }
                .severity-box { padding: 15px; border-radius: 5px; text-align: center; color: white; }
                .critical { background-color: #e74c3c; }
                .high { background-color: #e67e22; }
                .medium { background-color: #f39c12; }
                .low { background-color: #27ae60; }
                .project-card { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin: 10px 0; }
                .project-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
                .project-name { font-weight: bold; font-size: 18px; }
                .project-status { padding: 5px 10px; border-radius: 3px; color: white; font-size: 12px; }
                .status-completed { background-color: #28a745; }
                .status-error { background-color: #dc3545; }
                .status-no-files { background-color: #6c757d; }
                .findings-list { margin-top: 10px; }
                .finding-item { background-color: white; border-left: 4px solid #007bff; padding: 10px; margin: 5px 0; border-radius: 3px; }
                .finding-severity { font-weight: bold; }
                .severity-critical { color: #e74c3c; }
                .severity-high { color: #e67e22; }
                .severity-medium { color: #f39c12; }
                .severity-low { color: #27ae60; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Multi-Project Secret Scanner Report</h1>
                    <p><strong>Parent Directory:</strong> {{ parent_directory }}</p>
                    <p><strong>Scan Date:</strong> {{ scan_date }}</p>
                </div>
                
                <div class="summary-grid">
                    <div class="summary-card">
                        <h3>{{ projects_found }}</h3>
                        <p>Projects Found</p>
                    </div>
                    <div class="summary-card">
                        <h3>{{ projects_scanned }}</h3>
                        <p>Projects Scanned</p>
                    </div>
                    <div class="summary-card">
                        <h3>{{ total_findings }}</h3>
                        <p>Total Findings</p>
                    </div>
                    <div class="summary-card">
                        <h3>{{ overall_summary.files_affected|length }}</h3>
                        <p>Files Affected</p>
                    </div>
                </div>
                
                <h2>📊 Overall Severity Breakdown</h2>
                <div class="severity-grid">
                    <div class="severity-box critical">
                        <h3>{{ overall_summary.by_severity.get('critical', 0) }}</h3>
                        <p>Critical</p>
                    </div>
                    <div class="severity-box high">
                        <h3>{{ overall_summary.by_severity.get('high', 0) }}</h3>
                        <p>High</p>
                    </div>
                    <div class="severity-box medium">
                        <h3>{{ overall_summary.by_severity.get('medium', 0) }}</h3>
                        <p>Medium</p>
                    </div>
                    <div class="severity-box low">
                        <h3>{{ overall_summary.by_severity.get('low', 0) }}</h3>
                        <p>Low</p>
                    </div>
                </div>
                
                <h2>📁 Project Results</h2>
                {% for project in projects %}
                <div class="project-card">
                    <div class="project-header">
                        <div class="project-name">{{ project.project_name }}</div>
                        <div class="project-status status-{{ project.status }}">
                            {{ project.status.upper() }}
                        </div>
                    </div>
                    
                    <p><strong>Path:</strong> {{ project.project_path }}</p>
                    <p><strong>Findings:</strong> {{ project.summary.total_findings }}</p>
                    
                    {% if project.error %}
                    <p><strong>Error:</strong> {{ project.error }}</p>
                    {% endif %}
                    
                    {% if project.findings %}
                    <div class="findings-list">
                        <h4>Key Findings:</h4>
                        {% for finding in project.findings[:5] %}
                        <div class="finding-item">
                            <div class="finding-severity severity-{{ finding.severity }}">
                                {{ finding.severity.upper() }}: {{ finding.pattern_name }}
                            </div>
                            <div><strong>File:</strong> {{ finding.file_path.name }}</div>
                            <div><strong>Line:</strong> {{ finding.line_number }}</div>
                            <div><strong>Matched:</strong> {{ finding.matched_text[:100] }}{% if finding.matched_text|length > 100 %}...{% endif %}</div>
                        </div>
                        {% endfor %}
                        {% if project.findings|length > 5 %}
                        <p><em>... and {{ project.findings|length - 5 }} more findings</em></p>
                        {% endif %}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
                
                <div class="footer">
                    <p>This report was generated automatically by the Secret & PII Scanner.</p>
                    <p>For questions or support, please contact your security team.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return Template(template_str)
    
    def _get_html_template(self) -> Template:
        """Get HTML template for reports."""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secret Scanner Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .summary {
            padding: 30px;
            border-bottom: 1px solid #eee;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .summary-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .findings {
            padding: 30px;
        }
        .finding {
            margin-bottom: 30px;
            border: 1px solid #eee;
            border-radius: 8px;
            overflow: hidden;
        }
        .finding-header {
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #eee;
        }
        .finding-title {
            margin: 0;
            font-size: 1.2em;
            color: #333;
        }
        .finding-meta {
            margin: 10px 0 0 0;
            font-size: 0.9em;
            color: #666;
        }
        .finding-content {
            padding: 20px;
        }
        .severity-critical { color: #dc3545; }
        .severity-high { color: #fd7e14; }
        .severity-medium { color: #ffc107; }
        .severity-low { color: #28a745; }
        .matched-text {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            margin: 10px 0;
        }
        .context {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 15px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
        }
        .file-path {
            color: #667eea;
            font-weight: bold;
        }
        .no-findings {
            text-align: center;
            padding: 50px;
            color: #28a745;
            font-size: 1.2em;
        }
        .severity-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .severity-badge.critical { background: #dc3545; color: white; }
        .severity-badge.high { background: #fd7e14; color: white; }
        .severity-badge.medium { background: #ffc107; color: black; }
        .severity-badge.low { background: #28a745; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐Secret Scanner Report</h1>
            <p>Generated on {{ scan_timestamp }}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Scan Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Total Findings</h3>
                    <div class="number">{{ scan_summary.total_findings }}</div>
                </div>
                <div class="summary-card">
                    <h3>Files Affected</h3>
                    <div class="number">{{ scan_summary.files_affected|length }}</div>
                </div>
                {% for severity, count in scan_summary.by_severity.items() %}
                <div class="summary-card">
                    <h3>{{ severity.title() }}</h3>
                    <div class="number severity-{{ severity }}">{{ count }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="findings">
            <h2>🔍 Findings</h2>
            {% if findings %}
                {% for finding in findings %}
                <div class="finding">
                    <div class="finding-header">
                        <h3 class="finding-title">
                            {{ finding.pattern_name }}
                            <span class="severity-badge {{ finding.severity }}">{{ finding.severity }}</span>
                        </h3>
                        <div class="finding-meta">
                            <span class="file-path">{{ finding.file_path }}</span> | 
                            Line {{ finding.line_number }}, Column {{ finding.column }} | 
                            Category: {{ finding.category.title() }}
                        </div>
                    </div>
                    <div class="finding-content">
                        {% if finding.description %}
                        <p><strong>Description:</strong> {{ finding.description }}</p>
                        {% endif %}
                        
                        <p><strong>Matched Text:</strong></p>
                        <div class="matched-text">{{ finding.matched_text }}</div>
                        
                        <p><strong>Context:</strong></p>
                        <div class="context">{{ finding.context }}</div>
                        
                        {% if finding.entropy_score %}
                        <p><strong>Entropy Score:</strong> {{ "%.2f"|format(finding.entropy_score) }}</p>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-findings">
                    ✅ No secrets or PII found!
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
        """
        return Template(template_str) 
"""
Email notification utility for theSecrect scanner.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import os

class EmailNotifier:
    """Email notification system for Secret scanner reports."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email notifier with configuration.
        
        Args:
            config: Dictionary containing email configuration
                - smtp_server: SMTP server address
                - smtp_port: SMTP server port
                - username: Email username
                - password: Email password or app password
                - use_tls: Whether to use TLS (default: True)
                - from_email: Sender email address
                - to_emails: List of recipient email addresses
        """
        self.smtp_server = config.get('smtp_server', 'smtp.mailersend.net')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username', 'MS_QveQlC@test-eqvygm0rvy8l0p7w.mlsender.net')
        self.password = config.get('password', 'mssp.wHoUlmw.vywj2lpy23jl7oqz.t11GXa7')
        self.use_tls = config.get('use_tls', True)
        self.from_email = config.get('from_email', 'MS_QveQlC@test-eqvygm0rvy8l0p7w.mlsender.net')
        self.to_emails = config.get('to_emails', [])
        
        # Validate required configuration
        if not all([self.smtp_server, self.username, self.password, self.from_email]):
            raise ValueError("Missing required email configuration: smtp_server, username, password, from_email")
    
    def send_report_email(self, 
                         pdf_path: Path, 
                         scan_summary: Dict[str, Any],
                         project_name: str = "Secret Scanner Report") -> bool:
        """
        Send email with PDF report attachment.
        
        Args:
            pdf_path: Path to the PDF report file
            scan_summary: Summary of scan results
            project_name: Name of the project being scanned
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"🔐Secret Scanner Report - {project_name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Create email body
            body = self._create_email_body(scan_summary, project_name)
            msg.attach(MIMEText(body, 'html'))
            
            # Attach PDF file
            if pdf_path.exists():
                with open(pdf_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {pdf_path.name}'
                )
                msg.attach(part)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def _create_email_body(self, scan_summary: Dict[str, Any], project_name: str) -> str:
        """Create HTML email body with scan summary."""
        
        # Calculate severity counts
        critical_count = scan_summary.get('by_severity', {}).get('critical', 0)
        high_count = scan_summary.get('by_severity', {}).get('high', 0)
        medium_count = scan_summary.get('by_severity', {}).get('medium', 0)
        low_count = scan_summary.get('by_severity', {}).get('low', 0)
        total_findings = scan_summary.get('total_findings', 0)
        files_affected = len(scan_summary.get('files_affected', []))
        
        # Determine overall status
        if critical_count > 0 or high_count > 0:
            status_icon = "🔴"
            status_text = "CRITICAL - Immediate attention required"
            status_color = "#dc3545"
        elif medium_count > 0:
            status_icon = "🟡"
            status_text = "WARNING - Review recommended"
            status_color = "#ffc107"
        elif low_count > 0:
            status_icon = "🟢"
            status_text = "LOW RISK - Monitor"
            status_color = "#28a745"
        else:
            status_icon = "✅"
            status_text = "CLEAN - No issues found"
            status_color = "#28a745"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .status {{ font-size: 18px; font-weight: bold; margin: 10px 0; }}
                .summary {{ background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin-bottom: 20px; }}
                .severity-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
                .severity-box {{ padding: 15px; border-radius: 5px; text-align: center; color: white; }}
                .critical {{ background-color: #dc3545; }}
                .high {{ background-color: #fd7e14; }}
                .medium {{ background-color: #ffc107; color: #212529; }}
                .low {{ background-color: #28a745; }}
                .clean {{ background-color: #6c757d; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔐Secret Scanner Report</h1>
                <p><strong>Project:</strong> {project_name}</p>
                <p><strong>Scan Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="status" style="color: {status_color};">
                {status_icon} {status_text}
            </div>
            
            <div class="summary">
                <h2>📊 Scan Summary</h2>
                <div class="severity-grid">
                    <div class="severity-box critical">
                        <h3>{critical_count}</h3>
                        <p>Critical</p>
                    </div>
                    <div class="severity-box high">
                        <h3>{high_count}</h3>
                        <p>High</p>
                    </div>
                    <div class="severity-box medium">
                        <h3>{medium_count}</h3>
                        <p>Medium</p>
                    </div>
                    <div class="severity-box low">
                        <h3>{low_count}</h3>
                        <p>Low</p>
                    </div>
                </div>
                
                <p><strong>Total Findings:</strong> {total_findings}</p>
                <p><strong>Files Affected:</strong> {files_affected}</p>
            </div>
            
            <div class="summary">
                <h2>📋 What's Included</h2>
                <ul>
                    <li>Detailed findings with file locations and line numbers</li>
                    <li>Severity classification for each finding</li>
                    <li>Context around detectedSecrects and PII</li>
                    <li>Recommendations for remediation</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>This report was generated automatically by theSecrect & PII Scanner.</p>
                <p>For questions or support, please contact your security team.</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def test_connection(self) -> bool:
        """Test email connection and authentication."""
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.username, self.password)
            
            return True
            
        except Exception as e:
            print(f"Email connection test failed: {e}")
            return False
    
    def send_multi_project_email(self, 
                                main_pdf_path: Path, 
                                project_pdfs: Dict[str, Path],
                                scan_results: Dict[str, Any],
                                parent_directory_name: str = "Multi-Project Scan") -> bool:
        """
        Send email with multiple PDF attachments for multi-project scan.
        
        Args:
            main_pdf_path: Path to the main multi-project PDF report
            project_pdfs: Dictionary mapping project names to their PDF paths
            scan_results: Complete scan results from multi-project scanner
            parent_directory_name: Name of the parent directory being scanned
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"🔐 Multi-ProjectSecret Scanner Report - {parent_directory_name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Create email body
            body = self._create_multi_project_email_body(scan_results, parent_directory_name)
            msg.attach(MIMEText(body, 'html'))
            
            # Attach main PDF report
            if main_pdf_path.exists():
                with open(main_pdf_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {main_pdf_path.name}'
                )
                msg.attach(part)
            
            # Attach individual project PDFs
            for project_name, pdf_path in project_pdfs.items():
                if pdf_path.exists():
                    with open(pdf_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {project_name}_report.pdf'
                    )
                    msg.attach(part)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending multi-project email: {e}")
            return False
    
    def _create_multi_project_email_body(self, scan_results: Dict[str, Any], parent_directory_name: str) -> str:
        """Create HTML email body for multi-project scan results."""
        
        overall_summary = scan_results.get('overall_summary', {})
        projects = scan_results.get('projects', [])
        
        # Calculate severity counts
        critical_count = overall_summary.get('by_severity', {}).get('critical', 0)
        high_count = overall_summary.get('by_severity', {}).get('high', 0)
        medium_count = overall_summary.get('by_severity', {}).get('medium', 0)
        low_count = overall_summary.get('by_severity', {}).get('low', 0)
        total_findings = overall_summary.get('total_findings', 0)
        files_affected = len(overall_summary.get('files_affected', []))
        projects_found = scan_results.get('projects_found', 0)
        projects_scanned = scan_results.get('projects_scanned', 0)
        
        # Determine overall status
        if critical_count > 0 or high_count > 0:
            status_icon = "🔴"
            status_text = "CRITICAL - Immediate attention required"
            status_color = "#dc3545"
        elif medium_count > 0:
            status_icon = "🟡"
            status_text = "WARNING - Review recommended"
            status_color = "#ffc107"
        elif low_count > 0:
            status_icon = "🟢"
            status_text = "LOW RISK - Monitor"
            status_color = "#28a745"
        else:
            status_icon = "✅"
            status_text = "CLEAN - No issues found"
            status_color = "#28a745"
        
        # Create project summary table
        project_rows = ""
        for project in projects:
            if project['status'] == 'completed' and project['summary']['total_findings'] > 0:
                project_name = project['project_name']
                findings = project['summary']['total_findings']
                critical = project['summary']['by_severity'].get('critical', 0)
                high = project['summary']['by_severity'].get('high', 0)
                
                severity_class = "critical" if critical > 0 else "high" if high > 0 else "medium"
                project_rows += f"""
                <tr>
                    <td>{project_name}</td>
                    <td>{findings}</td>
                    <td class="{severity_class}">{critical + high}</td>
                </tr>
                """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .status {{ font-size: 18px; font-weight: bold; margin: 10px 0; }}
                .summary {{ background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin-bottom: 20px; }}
                .severity-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
                .severity-box {{ padding: 15px; border-radius: 5px; text-align: center; color: white; }}
                .critical {{ background-color: #dc3545; }}
                .high {{ background-color: #fd7e14; }}
                .medium {{ background-color: #ffc107; color: #212529; }}
                .low {{ background-color: #28a745; }}
                .clean {{ background-color: #6c757d; }}
                .project-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .project-table th, .project-table td {{ border: 1px solid #dee2e6; padding: 10px; text-align: left; }}
                .project-table th {{ background-color: #f8f9fa; font-weight: bold; }}
                .project-table .critical {{ background-color: #f8d7da; color: #721c24; }}
                .project-table .high {{ background-color: #fff3cd; color: #856404; }}
                .project-table .medium {{ background-color: #d1ecf1; color: #0c5460; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔐 Multi-ProjectSecret Scanner Report</h1>
                <p><strong>Parent Directory:</strong> {parent_directory_name}</p>
                <p><strong>Scan Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="status" style="color: {status_color};">
                {status_icon} {status_text}
            </div>
            
            <div class="summary">
                <h2>📊 Overall Summary</h2>
                <div class="severity-grid">
                    <div class="severity-box critical">
                        <h3>{critical_count}</h3>
                        <p>Critical</p>
                    </div>
                    <div class="severity-box high">
                        <h3>{high_count}</h3>
                        <p>High</p>
                    </div>
                    <div class="severity-box medium">
                        <h3>{medium_count}</h3>
                        <p>Medium</p>
                    </div>
                    <div class="severity-box low">
                        <h3>{low_count}</h3>
                        <p>Low</p>
                    </div>
                </div>
                
                <p><strong>Projects Found:</strong> {projects_found}</p>
                <p><strong>Projects Scanned:</strong> {projects_scanned}</p>
                <p><strong>Total Findings:</strong> {total_findings}</p>
                <p><strong>Files Affected:</strong> {files_affected}</p>
            </div>
            
            <div class="summary">
                <h2>📁 Projects with Findings</h2>
                <table class="project-table">
                    <thead>
                        <tr>
                            <th>Project Name</th>
                            <th>Total Findings</th>
                            <th>Critical/High</th>
                        </tr>
                    </thead>
                    <tbody>
                        {project_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="summary">
                <h2>📋 Attachments Included</h2>
                <ul>
                    <li><strong>Main Report:</strong> Overall summary with all projects</li>
                    <li><strong>Individual Reports:</strong> Detailed findings for each project with issues</li>
                    <li>Severity classification and remediation recommendations</li>
                    <li>File locations and context for each finding</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>This report was generated automatically by theSecrect & PII Scanner.</p>
                <p>For questions or support, please contact your security team.</p>
            </div>
        </body>
        </html>
        """
        
        return html_body 
"""
MailerSend API integration for sending emails
"""

import requests
import json
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class MailerSendAPI:
    """MailerSend API client for sending emails."""
    
    def __init__(self, api_token: str = "mlsn.6ba8c1d6d1b2e4a374ddc6dce508e88dd48f0e7b205b05d2318f9a546abb1c13"):
        """
        Initialize MailerSend API client.
        
        Args:
            api_token: MailerSend API token
        """
        self.api_token = api_token
        self.base_url = "https://api.mailersend.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def send_email(self, 
                   from_email: str,
                   to_email: str,
                   subject: str,
                   html_content: str,
                   text_content: Optional[str] = None,
                   attachments: Optional[List[Path]] = None) -> bool:
        """
        Send email using MailerSend API.
        
        Args:
            from_email: Sender email address
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (optional)
            attachments: List of file paths to attach (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Prepare email data
            email_data = {
                "from": {
                    "email": from_email
                },
                "to": [
                    {
                        "email": to_email
                    }
                ],
                "subject": subject,
                "html": html_content
            }
            
            # Add text content if provided
            if text_content:
                email_data["text"] = text_content
            
            # Add attachments if provided
            if attachments:
                email_data["attachments"] = []
                for attachment_path in attachments:
                    if attachment_path.exists():
                        try:
                            with open(attachment_path, 'rb') as f:
                                file_content = f.read()
                                file_base64 = base64.b64encode(file_content).decode('utf-8')
                                
                                email_data["attachments"].append({
                                    "content": file_base64,
                                    "filename": attachment_path.name,
                                    "type": self._get_mime_type(attachment_path)
                                })
                        except Exception as e:
                            print(f"Warning: Could not attach file {attachment_path}: {e}")
            
            # Send email
            response = requests.post(
                f"{self.base_url}/email",
                headers=self.headers,
                json=email_data,
                timeout=30
            )
            
            if response.status_code == 202:
                return True
            else:
                print(f"MailerSend API error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending email via API: {e}")
            return False
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for file."""
        extension = file_path.suffix.lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.html': 'text/html',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.csv': 'text/csv',
            '.xml': 'application/xml'
        }
        return mime_types.get(extension, 'application/octet-stream')
    
    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            response = requests.get(
                f"{self.base_url}/domains",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"API connection test failed: {e}")
            return False
    
    def send_report_email(self, 
                         pdf_path: Path,
                         scan_summary: Dict[str, Any],
                         project_name: str = "Secret Scanner Report",
                         from_email: str = "MS_QveQlC@test-eqvygm0rvy8l0p7w.mlsender.net",
                         to_email: str = "MS_QveQlC@test-eqvygm0rvy8l0p7w.mlsender.net") -> bool:
        """
        Send report email with PDF attachment.
        
        Args:
            pdf_path: Path to PDF report
            scan_summary: Scan results summary
            project_name: Name of the project
            from_email: Sender email
            to_email: Recipient email
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Create subject
            subject = f"🔐Secret Scanner Report - {project_name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Create HTML content
            html_content = self._create_email_html(scan_summary, project_name)
            
            # Create text content
            text_content = self._create_email_text(scan_summary, project_name)
            
            # Send email with attachment
            return self.send_email(
                from_email=from_email,
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=[pdf_path] if pdf_path.exists() else None
            )
            
        except Exception as e:
            print(f"Error sending report email: {e}")
            return False
    
    def _create_email_html(self, scan_summary: Dict[str, Any], project_name: str) -> str:
        """Create HTML email content."""
        
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
        
        html_content = f"""
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
                    <li>Context around detected secrets and PII</li>
                    <li>Recommendations for remediation</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>This report was generated automatically by the Secret & PII Scanner.</p>
                <p>Sent via MailerSend API for reliable delivery.</p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _create_email_text(self, scan_summary: Dict[str, Any], project_name: str) -> str:
        """Create plain text email content."""
        
        critical_count = scan_summary.get('by_severity', {}).get('critical', 0)
        high_count = scan_summary.get('by_severity', {}).get('high', 0)
        medium_count = scan_summary.get('by_severity', {}).get('medium', 0)
        low_count = scan_summary.get('by_severity', {}).get('low', 0)
        total_findings = scan_summary.get('total_findings', 0)
        files_affected = len(scan_summary.get('files_affected', []))
        
        text_content = f"""
Secret Scanner Report - {project_name}
Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SCAN SUMMARY:
Critical: {critical_count}
High: {high_count}
Medium: {medium_count}
Low: {low_count}

Total Findings: {total_findings}
Files Affected: {files_affected}

This report was generated automatically by the Secret & PII Scanner.
Please see the attached PDF for detailed findings.
        """
        
        return text_content.strip()
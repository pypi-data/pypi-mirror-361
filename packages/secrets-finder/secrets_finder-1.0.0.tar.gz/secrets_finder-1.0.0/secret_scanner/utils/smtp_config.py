"""
SMTP Configuration for MailerSend
"""

from typing import Dict, Any, List, Optional

class SMTPConfig:
    """SMTP configuration for MailerSend"""
    
    def __init__(self, 
                 smtp_server: str = "smtp.mailersend.net",
                 smtp_port: int = 587,
                 username: str = "MS_QveQlC@test-eqvygm0rvy8l0p7w.mlsender.net",
                 password: str = "mssp.wHoUlmw.vywj2lpy23jl7oqz.t11GXa7",
                 from_email: str = "MS_QveQlC@test-eqvygm0rvy8l0p7w.mlsender.net",
                 to_emails: Optional[List[str]] = None,
                 use_tls: bool = True):
        """
        Initialize SMTP configuration with MailerSend credentials.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port (587 or 2525)
            username: MailerSend username
            password: MailerSend password
            from_email: Sender email address
            to_emails: List of recipient email addresses
            use_tls: Whether to use TLS encryption
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails or []
        self.use_tls = use_tls
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'username': self.username,
            'password': self.password,
            'from_email': self.from_email,
            'to_emails': self.to_emails,
            'use_tls': self.use_tls
        }
    
    @classmethod
    def get_default_config(cls) -> "SMTPConfig":
        """Get default MailerSend configuration."""
        return cls()
    
    @classmethod
    def with_recipients(cls, recipients: List[str]) -> "SMTPConfig":
        """Create config with specific recipients."""
        config = cls.get_default_config()
        config.to_emails = recipients
        return config
"""
Configuration management for theSecrect & PII Scanner.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, validator
import os
import re

class DetectionPattern(BaseModel):
    """Represents a detection pattern for Secrects or PII."""
    name: str
    regex: str
    severity: str = "medium"  # low, medium, high, critical
    description: Optional[str] = None
    category: str = "secret"  #Secrect, pii, custom
    compiled_regex: Optional[re.Pattern] = None
    
    @validator('severity')
    def validate_severity(cls, v):
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v not in valid_severities:
            raise ValueError(f'Severity must be one of: {valid_severities}')
        return v
    
    class Config:
        arbitrary_types_allowed = True

class ScannerConfig(BaseModel):
    """Main configuration for theSecrect scanner."""
    patterns: List[DetectionPattern] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    include_patterns: List[str] = field(default_factory=list)
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    context_lines: int = 3
    enable_entropy_check: bool = True
    entropy_threshold: float = 4.8
    enable_ml_detection: bool = False
    ml_model_path: Optional[str] = None
    
    # Multi-threading settings
    max_workers: Optional[int] = None  # None = auto-detect based on CPU cores
    chunk_size: int = 10  # Number of files to process per thread batch
    
    # Whitelist settings
    whitelist_patterns: List[str] = field(default_factory=list)
    whitelist_files: List[str] = field(default_factory=list)
    
    # Debug settings
    show_skipped_files: bool = False
    
    class Config:
        extra = "forbid"
    
    def __init__(self, **data):
        super().__init__(**data)
        # Set default max_workers based on CPU cores if not specified
        if self.max_workers is None:
            self.max_workers = min(32, (os.cpu_count() or 1) + 4)
        
        # Compile regex patterns for efficiency
        for pattern in self.patterns:
            try:
                pattern.compiled_regex = re.compile(pattern.regex, re.IGNORECASE)
            except re.error as e:
                print(f"Warning: Invalid regex pattern '{pattern.name}': {e}")
                # Use a simple fallback pattern
                pattern.compiled_regex = re.compile(r".*", re.IGNORECASE)

class Config:
    """Configuration manager for theSecrect scanner."""
    
    DEFAULT_CONFIG = {
        "patterns": [
            # Critical Cloud Provider Secrets
            {"name": "AWS Access Key ID", "regex": r"AKIA[0-9A-Z]{16}", "severity": "critical", "description": "AWS Access Key ID", "category": "secret"},
            {"name": "AWS Secret Access Key", "regex": r"aws_secret_access_key\s*[=:]\s*[\"']?[A-Za-z0-9/+=]{40}[\"']?", "severity": "critical", "description": "AWS Secret Access Key assignment", "category": "secret"},
            {"name": "Google API Key", "regex": r"AIza[0-9A-Za-z\-_]{35}", "severity": "high", "description": "Google API Key", "category": "secret"},
            {"name": "Azure Storage Key", "regex": r"DefaultEndpointsProtocol=https;AccountName=[a-z0-9]+;AccountKey=[A-Za-z0-9+/=]+;EndpointSuffix=core\.windows\.net", "severity": "high", "description": "Azure Storage Account Key", "category": "secret"},
            {"name": "Alibaba Access Key ID", "regex": r"LTAI[0-9a-zA-Z]{16}", "severity": "high", "description": "Alibaba Cloud Access Key ID", "category": "secret"},
            {"name": "Alibaba Access Key Secret", "regex": r"alibaba[_-]?access[_-]?key[_-]?secret\s*[=:]\s*[\"']?[a-zA-Z0-9]{30}[\"']?", "severity": "high", "description": "Alibaba Cloud Access Key Secret assignment", "category": "secret"},
            {"name": "Oracle Cloud API Key", "regex": r"ocid1\.tenancy\.oc1..[a-zA-Z0-9_\-]+", "severity": "high", "description": "Oracle Cloud API Key", "category": "secret"},
            {"name": "IBM Cloud API Key", "regex": r"bx\.[a-z0-9]{64}", "severity": "high", "description": "IBM Cloud API Key", "category": "secret"},
            {"name": "DigitalOcean Token", "regex": r"dop_v1_[a-zA-Z0-9]{64}", "severity": "high", "description": "DigitalOcean API Token", "category": "secret"},
            
            # Payment Processing Secrets
            {"name": "Stripe Secret Key", "regex": r"sk_live_[0-9a-zA-Z]{24,}", "severity": "critical", "description": "Stripe live secret key", "category": "secret"},
            {"name": "Stripe Publishable Key", "regex": r"pk_live_[0-9a-zA-Z]{24,}", "severity": "medium", "description": "Stripe live publishable key", "category": "secret"},
            {"name": "PayPal Braintree Access Token", "regex": r"access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}", "severity": "high", "description": "PayPal Braintree Access Token", "category": "secret"},
            {"name": "Square Access Token", "regex": r"sq0atp-[0-9A-Za-z\-_]{22,43}", "severity": "high", "description": "Square Access Token", "category": "secret"},
            
            # Communication Platform Secrets
            {"name": "Slack Token", "regex": r"xox[baprs]-[0-9a-zA-Z]{10,48}", "severity": "high", "description": "Slack token", "category": "secret"},
            {"name": "Twilio API Key", "regex": r"twilio[_-]?api[_-]?key\s*[=:]\s*[\"']?SK[0-9a-fA-F]{32}[\"']?", "severity": "high", "description": "Twilio API Key assignment", "category": "secret"},
            {"name": "SendGrid API Key", "regex": r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}", "severity": "high", "description": "SendGrid API Key", "category": "secret"},
            {"name": "Mailgun API Key", "regex": r"key-[0-9a-zA-Z]{32}", "severity": "high", "description": "Mailgun API Key", "category": "secret"},
            {"name": "Mailchimp API Key", "regex": r"[0-9a-f]{32}-us[0-9]{1,2}", "severity": "high", "description": "Mailchimp API Key", "category": "secret"},
            {"name": "Sendinblue API Key", "regex": r"xkeysib-[a-zA-Z0-9]{64}", "severity": "high", "description": "Sendinblue API Key", "category": "secret"},
            
            # Development Platform Secrets
            {"name": "GitHub Token", "regex": r"gh[pousr]_[A-Za-z0-9]{36,255}", "severity": "high", "description": "GitHub token (personal/app/oauth/refresh)", "category": "secret"},
            {"name": "Heroku API Key", "regex": r"heroku[_-]?api[_-]?key\s*[=:]\s*[\"']?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}[\"']?", "severity": "high", "description": "Heroku API Key assignment", "category": "secret"},
            {"name": "Bitbucket App Password", "regex": r"bbp_[A-Za-z0-9]{32}", "severity": "high", "description": "Bitbucket App Password", "category": "secret"},
            {"name": "Atlassian API Token", "regex": r"[A-Za-z0-9]{24}\.[A-Za-z0-9]{24}", "severity": "high", "description": "Atlassian API Token", "category": "secret"},
            
            # Cloud Services Secrets
            {"name": "Cloudflare API Token", "regex": r"cloudflare[_-]?api[_-]?token\s*[=:]\s*[\"']?[a-zA-Z0-9]{37}[\"']?", "severity": "high", "description": "Cloudflare API Token assignment", "category": "secret"},
            {"name": "Shopify Access Token", "regex": r"shpat_[0-9a-fA-F]{32,}", "severity": "high", "description": "Shopify Access Token", "category": "secret"},
            {"name": "Algolia API Key", "regex": r"algolia[_-]?api[_-]?key\s*[=:]\s*[\"']?[a-z0-9]{32}\.[a-z0-9]{8,}[\"']?", "severity": "high", "description": "Algolia API Key assignment", "category": "secret"},
            {"name": "Firebase Server Key", "regex": r"AAAA[a-zA-Z0-9_-]{7}:[a-zA-Z0-9_-]{140}", "severity": "high", "description": "Firebase Cloud Messaging Server Key", "category": "secret"},
            {"name": "Dropbox API Key", "regex": r"sl\.[A-Za-z0-9_-]{15,}", "severity": "high", "description": "Dropbox API Key", "category": "secret"},
            
            # Authentication & Identity Secrets
            {"name": "Okta API Token", "regex": r"00[a-zA-Z0-9]{20}\$[a-zA-Z0-9]{28}", "severity": "high", "description": "Okta API Token", "category": "secret"},
            {"name": "JWT Token", "regex": r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*", "severity": "high", "description": "JWT token", "category": "secret"},
            {"name": "Google OAuth Access Token", "regex": r"ya29\.[0-9A-Za-z\-_]+", "severity": "high", "description": "Google OAuth 2.0 Access Token", "category": "secret"},
            {"name": "Facebook Access Token", "regex": r"EAACEdEose0cBA[0-9A-Za-z]+", "severity": "high", "description": "Facebook Graph API Access Token", "category": "secret"},
            {"name": "Twitter Bearer Token", "regex": r"AAAAAAAAAAAAAAAAAAAAA[A-Za-z0-9]{35,}", "severity": "high", "description": "Twitter Bearer Token", "category": "secret"},
            {"name": "Zoom JWT Token", "regex": r"[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}", "severity": "high", "description": "Zoom JWT Token", "category": "secret"},
            
            # Database & Storage Secrets
            {"name": "Database URL", "regex": r"(mysql|postgresql|mongodb|redis)://[a-zA-Z0-9._%+-]+:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(:[0-9]+)?/[a-zA-Z0-9._/-]+", "severity": "high", "description": "Database connection string", "category": "secret"},
            {"name": "Password Assignment", "regex": r"password\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Password assignment", "category": "secret"},
            {"name": "DB Password", "regex": r"db[_-]?password\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Database password assignment", "category": "secret"},
            {"name": "MySQL Password", "regex": r"mysql[_-]?password\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "MySQL password assignment", "category": "secret"},
            {"name": "PostgreSQL Password", "regex": r"postgres[_-]?password\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "PostgreSQL password assignment", "category": "secret"},
            {"name": "Redis Password", "regex": r"redis[_-]?password\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Redis password assignment", "category": "secret"},
            {"name": "MongoDB Password", "regex": r"mongo[_-]?password\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "MongoDB password assignment", "category": "secret"},
            
            # Private Keys (Critical)
            {"name": "RSA Private Key", "regex": r"-----BEGIN RSA PRIVATE KEY-----[\s\S]+?-----END RSA PRIVATE KEY-----", "severity": "critical", "description": "RSA private key block", "category": "secret"},
            {"name": "SSH Private Key", "regex": r"-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]+?-----END OPENSSH PRIVATE KEY-----", "severity": "critical", "description": "OpenSSH private key block", "category": "secret"},
            {"name": "DSA Private Key", "regex": r"-----BEGIN DSA PRIVATE KEY-----[\s\S]+?-----END DSA PRIVATE KEY-----", "severity": "critical", "description": "DSA private key block", "category": "secret"},
            {"name": "EC Private Key", "regex": r"-----BEGIN EC PRIVATE KEY-----[\s\S]+?-----END EC PRIVATE KEY-----", "severity": "critical", "description": "EC private key block", "category": "secret"},
            {"name": "PGP Private Key", "regex": r"-----BEGIN PGP PRIVATE KEY BLOCK-----[\s\S]+?-----END PGP PRIVATE KEY BLOCK-----", "severity": "critical", "description": "PGP private key block", "category": "secret"},
            
            # Generic Secret Assignments
            {"name": "Generic API Key", "regex": r"api[_-]?key\s*[=:]\s*[\"']?[a-zA-Z0-9]{16,}[\"']?", "severity": "high", "description": "Generic API key assignment", "category": "secret"},
            {"name": "OAuth Access Token", "regex": r"access_token\s*[=:]\s*[\"']?[a-zA-Z0-9\-\._~\+\/]+=*[\"']?", "severity": "medium", "description": "OAuth access token assignment", "category": "secret"},
            {"name": "Passwd Assignment", "regex": r"passwd\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to passwd variable", "category": "secret"},
            {"name": "Pwd Assignment", "regex": r"pwd\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to pwd variable", "category": "secret"},
            {"name": "Secret Assignment", "regex": r"secret\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to secret variable", "category": "secret"},
            {"name": "Token Assignment", "regex": r"token\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to token variable", "category": "secret"},
            {"name": "Access Key Assignment", "regex": r"access[_-]?key\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to access_key variable", "category": "secret"},
            {"name": "API Secret Assignment", "regex": r"api[_-]?secret\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to api_secret variable", "category": "secret"},
            {"name": "Client Secret Assignment", "regex": r"client[_-]?secret\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to client_secret variable", "category": "secret"},
            {"name": "App Secret Assignment", "regex": r"app[_-]?secret\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to app_secret variable", "category": "secret"},
            {"name": "Master Key Assignment", "regex": r"master[_-]?key\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to master_key variable", "category": "secret"},
            {"name": "Encryption Key Assignment", "regex": r"encryption[_-]?key\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to encryption_key variable", "category": "secret"},
            {"name": "Private Key Assignment", "regex": r"private[_-]?key\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to private_key variable", "category": "secret"},
            {"name": "Credential Assignment", "regex": r"credential\s*[=:]\s*[\"']?[^\"'\s]{8,}[\"']?", "severity": "high", "description": "Assignment to credential variable", "category": "secret"},
            
            # Project Management & Collaboration Tools
            {"name": "Trello API Key", "regex": r"trello[_-]?api[_-]?key\s*[=:]\s*[\"']?[a-f0-9]{32}[\"']?", "severity": "high", "description": "Trello API Key assignment", "category": "secret"},
            {"name": "Asana Personal Access Token", "regex": r"0/[0-9a-z]{32}", "severity": "high", "description": "Asana Personal Access Token", "category": "secret"},
            {"name": "PagerDuty API Key", "regex": r"pagerduty[_-]?api[_-]?key\s*[=:]\s*[\"']?P[A-Z0-9]{7}[\"']?", "severity": "high", "description": "PagerDuty API Key assignment", "category": "secret"},
            {"name": "Zendesk API Token", "regex": r"zendesk[_-]?api[_-]?token\s*[=:]\s*[\"']?[a-zA-Z0-9]{40}[\"']?", "severity": "high", "description": "Zendesk API Token assignment", "category": "secret"},
            
            # Event & Ticketing Platforms
            {"name": "Picatic API Key", "regex": r"picatic[_-]?api[_-]?key\s*[=:]\s*[\"']?sk_live_[0-9a-z]{32}[\"']?", "severity": "high", "description": "Picatic API Key assignment", "category": "secret"},
            
            # PII Patterns
            {"name": "Email Address", "regex": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "severity": "medium", "description": "Email address", "category": "pii"},
            {"name": "Credit Card Number", "regex": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b", "severity": "high", "description": "Credit card number (Visa, MasterCard, Amex, Discover, JCB, Diners Club)", "category": "pii"},
            {"name": "Credit Card with Context", "regex": r"(?:credit[_-]?card|cc[_-]?num|card[_-]?number|payment[_-]?card)\s*[=:]\s*[\"']?(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})[\"']?", "severity": "high", "description": "Credit card number in variable assignment context", "category": "pii"},
            {"name": "SSN (US)", "regex": r"\b\d{3}-\d{2}-\d{4}\b", "severity": "critical", "description": "US Social Security Number", "category": "pii"},
            {"name": "IP Address", "regex": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", "severity": "low", "description": "IPv4 address", "category": "pii"},
            {"name": "MAC Address", "regex": r"\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b", "severity": "low", "description": "MAC address", "category": "pii"},
        ],
        "exclude_patterns": [
            # Binary and compiled files
            "*.exe", "*.dll", "*.so", "*.dylib", "*.bin", "*.pyc", "*.pyo",
            
            # Large data files
            "*.dat", "*.db", "*.sqlite", "*.sqlite3",
            
            # Media files
            "*.mp3", "*.mp4", "*.avi", "*.mov", "*.wmv", "*.flv", "*.webm",
            "*.wav", "*.flac", "*.ogg",
            
            # Font files
            "*.ttf", "*.otf", "*.woff", "*.woff2", "*.eot",
            
            # Image files
            "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.ico", "*.svg", "*.tiff", "*.tga", "*.webp",
            
            # Archive files
            "*.zip", "*.tar", "*.gz", "*.rar", "*.7z",
            
            # Generated files
            "*.min.js", "*.min.css", "*.map",
            
            # Lock files (but keep package.json, requirements.txt, etc.)
            "package-lock.json", "yarn.lock", "*.lock",
            
            # Test files (optional - can be overridden)
            "*.test.js", "*.spec.js", "*.test.py", "*.spec.py",
            
            # Cache directories
            "__pycache__/", ".pytest_cache/", "node_modules/", "vendor/",
            
            # Version control
            ".git/",
            
            # Temporary files
            "*.log", "*.tmp", "*.cache"
        ],
        "include_patterns": [
            "*.py",
            "*.js",
            "*.ts",
            "*.jsx",
            "*.tsx",
            "*.java",
            "*.c",
            "*.cpp",
            "*.h",
            "*.hpp",
            "*.go",
            "*.rs",
            "*.php",
            "*.rb",
            "*.sh",
            "*.bash",
            "*.zsh",
            "*.fish",
            "*.env",
            "*.venv",
            "*.config",
            "*.conf",
            "*.ini",
            "*.yaml",
            "*.yml",
            "*.json",
            "*.xml",
            "*.html",
            "*.css",
            "*.scss",
            "*.sass",
            "*.md",
            "*.txt",
            "*.toml",
            "*.properties",
            "*.cfg",
            "*.cnf",
            "*.cnf",
            "*.conf",
            "*.config",
            "*.ini",
            "*.properties",
            "*.props",
            "*.xml",
            "*.yaml",
            "*.yml",
            "*.json",
            "*.json5",
            "*.jsonc",
            "*.toml",
            "*.hcl",
            "*.tf",
            "*.tfvars",
            "*.tfstate",
            "*.tfstate.backup",
            "*.lock.hcl",
            "*.tfplan",
            "*.tfvars.json",
            "*.auto.tfvars",
            "*.auto.tfvars.json",
            "*.override.tf",
            "*.override.tf.json",
            "*.tf.json",
            "*.tfvars.json",
            "*.tfstate.json",
            "*.tfstate.backup.json",
            "*.lock.hcl.json",
            "*.tfplan.json",
            "*.auto.tfvars.json",
            "*.override.tf.json",
            "*.tf.json",
            "*.tfvars.json",
            "*.tfstate.json",
            "*.tfstate.backup.json",
            "*.lock.hcl.json",
            "*.tfplan.json",
            "*.auto.tfvars.json",
            "*.override.tf.json"
        ],
        "max_file_size": 10485760,  # 10MB
        "context_lines": 3,
        "enable_entropy_check": True,
        "entropy_threshold": 4.8,
        "enable_ml_detection": False
    }
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> ScannerConfig:
        """Load configuration from file or use defaults."""
        if config_path is not None:
            config_file = Path(config_path)
            if config_file.exists():
                with open(str(config_file), 'r') as f:
                    config_data = yaml.safe_load(f)
                    return ScannerConfig(**config_data)
        
        # Try to find config in current directory
        default_config_paths = [
            Path(".secret-scanner.yaml"),
            Path(".secret-scanner.yml"),
            Path("secret-scanner.yaml"),
            Path("secret-scanner.yml")
        ]
        
        for config_file in default_config_paths:
            if config_file.exists():
                with open(str(config_file), 'r') as f:
                    config_data = yaml.safe_load(f)
                    return ScannerConfig(**config_data)
        
        # Use default configuration
        return cls.create_default()
    
    @classmethod
    def create_default(cls) -> ScannerConfig:
        """Create default configuration."""
        patterns = [DetectionPattern(**pattern) for pattern in cls.DEFAULT_CONFIG["patterns"]]
        
        return ScannerConfig(
            patterns=patterns,
            exclude_patterns=cls.DEFAULT_CONFIG["exclude_patterns"],
            include_patterns=cls.DEFAULT_CONFIG["include_patterns"],
            max_file_size=cls.DEFAULT_CONFIG["max_file_size"],
            context_lines=cls.DEFAULT_CONFIG["context_lines"],
            enable_entropy_check=cls.DEFAULT_CONFIG["enable_entropy_check"],
            entropy_threshold=cls.DEFAULT_CONFIG["entropy_threshold"],
            enable_ml_detection=cls.DEFAULT_CONFIG["enable_ml_detection"]
        )
    
    @classmethod
    def load_default(cls) -> ScannerConfig:
        """Load default configuration."""
        return cls.create_default()
    
    @staticmethod
    def save(config: ScannerConfig, config_path: Path) -> None:
        """Save configuration to file."""
        config_data = config.dict()
        
        # Convert patterns to dict format for YAML
        config_data["patterns"] = [pattern.dict() for pattern in config.patterns]
        
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2) 
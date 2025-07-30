"""
Configuration management for the email server.
"""

import configparser
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration manager for the email server."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file. If None, looks for cfg.ini in current directory.
        """
        self.config = configparser.ConfigParser()
        
        # Set default values
        self._set_defaults()
        
        # Load from file if exists
        if config_file is None:
            config_file = "cfg.ini"
        
        if os.path.exists(config_file):
            self.config.read(config_file)
        
        # Override with environment variables if set
        self._load_from_env()
    
    def _set_defaults(self):
        """Set default configuration values."""
        self.config.add_section('smtpd')
        self.config.set('smtpd', 'host', '::')  # Listen on all interfaces (IPv4 and IPv6)
        self.config.set('smtpd', 'port', '25')

        self.config.add_section('rest')
        self.config.set('rest', 'port', '14000')
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # SMTP configuration
        if 'SMTP_HOST' in os.environ:
            self.config.set('smtpd', 'host', os.environ['SMTP_HOST'])
        if 'SMTP_PORT' in os.environ:
            self.config.set('smtpd', 'port', os.environ['SMTP_PORT'])
        
        # REST API configuration
        if 'REST_PORT' in os.environ:
            self.config.set('rest', 'port', os.environ['REST_PORT'])
    
    @property
    def smtp_host(self) -> str:
        """Get SMTP server host."""
        return self.config.get('smtpd', 'host')
    
    @property
    def smtp_port(self) -> int:
        """Get SMTP server port."""
        return self.config.getint('smtpd', 'port')
    
    @property
    def rest_host(self) -> str:
        """Get REST API host (same as SMTP host)."""
        return self.smtp_host
    
    @property
    def rest_port(self) -> int:
        """Get REST API port."""
        return self.config.getint('rest', 'port')
    
    def save(self, config_file: str = "cfg.ini"):
        """
        Save current configuration to file.
        
        Args:
            config_file: Path to save configuration file.
        """
        with open(config_file, 'w') as f:
            self.config.write(f)

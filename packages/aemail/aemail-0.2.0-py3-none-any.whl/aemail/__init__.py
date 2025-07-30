"""
AEmail - A simple SMTP server for receiving emails

A simple SMTP server that receives emails and provides REST API access.
"""

__version__ = "0.1.0"
__author__ = "lycying"
__description__ = "A simple SMTP server for receiving emails with REST API"

from .server import EmailServer
from .config import Config

__all__ = ["EmailServer", "Config"]

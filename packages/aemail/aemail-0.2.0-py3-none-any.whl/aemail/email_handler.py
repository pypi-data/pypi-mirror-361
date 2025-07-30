"""
Email processing and SMTP handler.
"""

import email
import logging
from email.header import decode_header
from typing import Dict, Any

from .data import EmailData


logger = logging.getLogger(__name__)


class EmailProcessor:
    """Email content processor."""
    
    @staticmethod
    def decode_header_value(header_value: str) -> str:
        """
        Decode email header value.
        
        Args:
            header_value: Raw header value
            
        Returns:
            Decoded string
        """
        if not header_value:
            return ""
        
        try:
            decoded_parts = decode_header(header_value)
            value, charset = decoded_parts[0]
            
            if charset and isinstance(value, bytes):
                return value.decode(charset)
            elif isinstance(value, bytes):
                return value.decode('utf-8', errors='ignore')
            else:
                return str(value)
        except Exception as e:
            logger.warning(f"Failed to decode header '{header_value}': {e}")
            return str(header_value)
    
    @staticmethod
    def guess_charset(message_part) -> str:
        """
        Guess the charset of a message part.
        
        Args:
            message_part: Email message part
            
        Returns:
            Charset name or 'utf-8' as fallback
        """
        charset = message_part.get_charset()
        if charset:
            return str(charset)
        
        content_type = message_part.get('Content-Type', '').lower()
        charset_pos = content_type.find('charset=')
        if charset_pos >= 0:
            charset = content_type[charset_pos + 8:].strip()
            # Remove quotes and semicolons
            charset = charset.strip('"\'').split(';')[0]
            return charset
        
        return 'utf-8'
    
    @classmethod
    def extract_text_content(cls, message_part) -> str:
        """
        Extract text content from a message part.
        
        Args:
            message_part: Email message part
            
        Returns:
            Extracted text content
        """
        content_type = message_part.get_content_type()
        
        if content_type not in ('text/plain', 'text/html'):
            return f"[{content_type}]"
        
        try:
            content = message_part.get_payload(decode=True)
            if isinstance(content, bytes):
                charset = cls.guess_charset(message_part)
                content = content.decode(charset, errors='ignore')
            return str(content)
        except Exception as e:
            logger.warning(f"Failed to extract content from {content_type}: {e}")
            return f"[Error extracting {content_type}]"
    
    @classmethod
    def process_message_content(cls, message) -> str:
        """
        Process and extract all text content from an email message.
        
        Args:
            message: Email message object
            
        Returns:
            Combined text content
        """
        content_parts = []
        
        if message.is_multipart():
            for part in message.get_payload():
                if part.is_multipart():
                    content_parts.append(cls.process_message_content(part))
                else:
                    content_parts.append(cls.extract_text_content(part))
        else:
            content_parts.append(cls.extract_text_content(message))
        
        return '\n'.join(filter(None, content_parts))


class SMTPHandler:
    """SMTP server handler for receiving emails."""
    
    def __init__(self, data_store: EmailData):
        """
        Initialize SMTP handler.
        
        Args:
            data_store: EmailData instance for storing messages
        """
        self.data_store = data_store
        self.processor = EmailProcessor()
    
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        """
        Handle RCPT TO command.
        
        Accept all recipients (wildcard email server).
        """
        envelope.rcpt_tos.append(address)
        logger.info(f"Accepting recipient: {address}")
        return '250 OK'
    
    async def handle_DATA(self, server, session, envelope):
        """
        Handle DATA command - process the email content.
        """
        try:
            # Parse email message
            message = email.message_from_bytes(envelope.content)
            
            # Extract message components
            mail_from = envelope.mail_from
            rcpt_tos = envelope.rcpt_tos
            subject = self.processor.decode_header_value(message.get('Subject', ''))
            content = self.processor.process_message_content(message)
            
            # Create message object
            email_data = {
                "from": mail_from,
                "to": rcpt_tos,
                "subject": subject,
                "content": content
            }
            
            # Store message
            self.data_store.store_message(email_data)
            
            logger.info(f"Stored message: {mail_from} -> {rcpt_tos} | {subject}")
            
            return '250 Message accepted for delivery'
            
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return '451 Requested action aborted: error in processing'

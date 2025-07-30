"""
REST API for accessing stored emails.
"""

import json
import logging
import os
from flask import Flask, jsonify, send_file
from pathlib import Path
from typing import Optional

from .data import EmailData


logger = logging.getLogger(__name__)


class EmailAPI:
    """REST API for email access."""
    
    def __init__(self, data_store: EmailData, static_dir: Optional[str] = None):
        """
        Initialize the email API.

        Args:
            data_store: EmailData instance for accessing stored emails
            static_dir: Directory containing static files (optional)
        """
        self.app = Flask(__name__)
        self.data_store = data_store

        # Default to package's static directory
        if static_dir is None:
            package_dir = os.path.dirname(os.path.abspath(__file__))
            self.static_dir = os.path.join(package_dir, "static")
        else:
            self.static_dir = static_dir
        
        # Configure JSON serialization
        self.app.json.ensure_ascii = False
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes."""
        
        @self.app.route('/')
        def index():
            """Serve the main page."""
            try:
                static_path = Path(self.static_dir) / 'index.html'
                if static_path.exists():
                    return send_file(str(static_path))
                else:
                    return self._create_default_page()
            except Exception as e:
                logger.error(f"Error serving index page: {e}")
                return self._create_default_page()
        
        @self.app.route('/all')
        def get_all_messages():
            """Get all stored messages."""
            try:
                messages = self.data_store.get_all_messages()
                return jsonify(messages)
            except Exception as e:
                logger.error(f"Error retrieving all messages: {e}")
                return jsonify({"error": "Failed to retrieve messages"}), 500
        
        @self.app.route('/from/<path:sender>')
        def get_messages_from(sender: str):
            """Get messages from a specific sender."""
            try:
                messages = self.data_store.get_messages_from(sender)
                return jsonify(messages)
            except Exception as e:
                logger.error(f"Error retrieving messages from {sender}: {e}")
                return jsonify({"error": "Failed to retrieve messages"}), 500
        
        @self.app.route('/to/<path:recipient>')
        def get_messages_to(recipient: str):
            """Get messages to a specific recipient."""
            try:
                messages = self.data_store.get_messages_to(recipient)
                return jsonify(messages)
            except Exception as e:
                logger.error(f"Error retrieving messages to {recipient}: {e}")
                return jsonify({"error": "Failed to retrieve messages"}), 500
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint."""
            return jsonify({"status": "healthy", "service": "aemail"})
    
    def _create_default_page(self) -> str:
        """Create a default HTML page when static files are not available."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AEmail Server</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                code { background: #e8e8e8; padding: 2px 4px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AEmail Server</h1>
                <p>Welcome to the email receive server API!</p>
                
                <h2>Available Endpoints:</h2>
                
                <div class="endpoint">
                    <strong>GET /all</strong><br>
                    Get all stored messages (last 100)
                </div>
                
                <div class="endpoint">
                    <strong>GET /from/&lt;email&gt;</strong><br>
                    Get messages from a specific sender<br>
                    Example: <code>/from/test@example.com</code>
                </div>
                
                <div class="endpoint">
                    <strong>GET /to/&lt;email&gt;</strong><br>
                    Get messages to a specific recipient<br>
                    Example: <code>/to/user@example.com</code>
                </div>
                
                <div class="endpoint">
                    <strong>GET /health</strong><br>
                    Health check endpoint
                </div>
                
                <h2>Usage Example:</h2>
                <p>Send an email to any address ending with your domain, then query:</p>
                <code>curl http://localhost:14000/to/test@yourdomain.com</code>
            </div>
        </body>
        </html>
        """
    
    def run(self, host: str = '127.0.0.1', port: int = 14000, debug: bool = False):
        """
        Run the Flask application.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
        logger.info(f"Starting web API on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

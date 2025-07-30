"""
Main email server implementation.
"""

import logging
import signal
import sys
import threading
from typing import Optional

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP

from .config import Config
from .data import EmailData
from .email_handler import SMTPHandler
from .web_api import EmailAPI


logger = logging.getLogger(__name__)


class EmailServer:
    """Main email server that combines SMTP and REST API functionality."""
    
    def __init__(self, config: Optional[Config] = None, db_path: Optional[str] = None):
        """
        Initialize the email server.
        
        Args:
            config: Configuration object. If None, creates default config.
            db_path: Path to SQLite database. If None, uses in-memory database.
        """
        self.config = config or Config()
        self.data_store = EmailData(db_path)
        self.smtp_handler = SMTPHandler(self.data_store)
        self.web_api = EmailAPI(self.data_store)
        
        # SMTP controller
        self.smtp_controller = None
        
        # Web server thread
        self.web_thread = None
        self._shutdown_event = threading.Event()
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _run_web_server(self):
        """Run the web server in a separate thread."""
        try:
            self.web_api.run(
                host=self.config.rest_host,
                port=self.config.rest_port,
                debug=False
            )
        except Exception as e:
            logger.error(f"Web server error: {e}")
            self._shutdown_event.set()
    
    def start(self):
        """Start both SMTP and web servers."""
        try:
            # Start SMTP server
            logger.info(f"Starting SMTP server on {self.config.smtp_host}:{self.config.smtp_port}")
            self.smtp_controller = Controller(
                self.smtp_handler,
                hostname=self.config.smtp_host,
                port=self.config.smtp_port
            )
            # Enable UTF8 support
            self.smtp_controller.factory = lambda: SMTP(self.smtp_handler, enable_SMTPUTF8=True)
            self.smtp_controller.start()
            
            # Start web server in a separate thread
            logger.info(f"Starting web API on {self.config.rest_host}:{self.config.rest_port}")
            self.web_thread = threading.Thread(target=self._run_web_server, daemon=True)
            self.web_thread.start()
            
            logger.info("Email server started successfully")
            logger.info(f"SMTP: {self.config.smtp_host}:{self.config.smtp_port}")
            logger.info(f"Web API: http://{self.config.rest_host}:{self.config.rest_port}")
            
            # Wait for shutdown signal
            self._wait_for_shutdown()
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            self.stop()
            raise
    
    def _wait_for_shutdown(self):
        """Wait for shutdown signal or web server error."""
        try:
            while not self._shutdown_event.is_set():
                if self.web_thread and not self.web_thread.is_alive():
                    logger.error("Web server thread died")
                    break
                self._shutdown_event.wait(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
    
    def stop(self):
        """Stop both servers and cleanup resources."""
        logger.info("Stopping email server...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Stop SMTP server
        if self.smtp_controller:
            try:
                self.smtp_controller.stop()
                logger.info("SMTP server stopped")
            except Exception as e:
                logger.error(f"Error stopping SMTP server: {e}")
        
        # Close database connection
        if self.data_store:
            try:
                self.data_store.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database: {e}")
        
        logger.info("Email server stopped")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

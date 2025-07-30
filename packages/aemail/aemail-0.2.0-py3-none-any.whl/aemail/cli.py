"""
Command line interface for the AEmail server.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .config import Config
from .server import EmailServer


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="aemail-server",
        description="A simple SMTP server for receiving emails with REST API access",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server with default settings
  aemail-server

  # Start server with custom config file
  aemail-server --config /path/to/config.ini

  # Start server with custom ports
  aemail-server --smtp-port 2525 --rest-port 8080

  # Start server with persistent database
  aemail-server --db-file /path/to/emails.db

  # Start server with debug logging
  aemail-server --verbose

Environment Variables:
  SMTP_HOST     - SMTP server host (default: :: - all interfaces)
  SMTP_PORT     - SMTP server port (default: 25)
  REST_PORT     - REST API port (default: 14000)
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file (default: cfg.ini)"
    )
    
    parser.add_argument(
        "--smtp-host",
        type=str,
        help="SMTP server host (overrides config file)"
    )
    
    parser.add_argument(
        "--smtp-port",
        type=int,
        help="SMTP server port (overrides config file)"
    )
    
    parser.add_argument(
        "--rest-port",
        type=int,
        help="REST API port (overrides config file)"
    )
    
    parser.add_argument(
        "--db-file",
        type=str,
        help="SQLite database file path (default: in-memory database)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    return parser


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Reduce noise from external libraries
    if not verbose:
        logging.getLogger('aiosmtpd').setLevel(logging.WARNING)
        logging.getLogger('werkzeug').setLevel(logging.WARNING)


def validate_args(args) -> None:
    """Validate command line arguments."""
    if args.smtp_port is not None and (args.smtp_port < 1 or args.smtp_port > 65535):
        raise ValueError("SMTP port must be between 1 and 65535")
    
    if args.rest_port is not None and (args.rest_port < 1 or args.rest_port > 65535):
        raise ValueError("REST port must be between 1 and 65535")
    
    if args.config and not Path(args.config).exists():
        raise FileNotFoundError(f"Configuration file not found: {args.config}")
    
    if args.db_file:
        db_path = Path(args.db_file)
        if not db_path.parent.exists():
            raise FileNotFoundError(f"Database directory does not exist: {db_path.parent}")


def create_config(args) -> Config:
    """Create configuration from command line arguments."""
    # Load base configuration
    config = Config(args.config)
    
    # Override with command line arguments
    if args.smtp_host:
        config.config.set('smtpd', 'host', args.smtp_host)
    
    if args.smtp_port:
        config.config.set('smtpd', 'port', str(args.smtp_port))
    
    if args.rest_port:
        config.config.set('rest', 'port', str(args.rest_port))
    
    return config


def main():
    """Main entry point for the command line interface."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Setup logging
        setup_logging(args.verbose)
        
        # Validate arguments
        validate_args(args)
        
        # Create configuration
        config = create_config(args)
        
        # Print startup information
        logger = logging.getLogger(__name__)
        logger.info("Starting AEmail Server")
        logger.info(f"SMTP: {config.smtp_host}:{config.smtp_port}")

        # Format URL correctly for IPv6
        web_host = config.rest_host
        if ':' in web_host and not web_host.startswith('['):
            # IPv6 address needs brackets in URL
            web_url = f"http://[{web_host}]:{config.rest_port}"
        else:
            web_url = f"http://{web_host}:{config.rest_port}"
        logger.info(f"REST API: {web_url}")
        
        if args.db_file:
            logger.info(f"Database: {args.db_file}")
        else:
            logger.info("Database: in-memory")
        
        # Create and start server
        with EmailServer(config=config, db_path=args.db_file) as server:
            server.start()
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

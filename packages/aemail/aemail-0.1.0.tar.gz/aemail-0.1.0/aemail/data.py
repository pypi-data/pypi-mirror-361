"""
Data access layer for email storage and retrieval.
"""

import datetime
import json
import sqlite3
from typing import Dict, List, Any, Optional
from pathlib import Path


class EmailData:
    """Data access object for email storage and retrieval."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the data access layer.
        
        Args:
            db_path: Path to SQLite database file. If None, uses in-memory database.
        """
        if db_path is None:
            self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            # Ensure directory exists
            db_file = Path(db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(str(db_file), check_same_thread=False)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS msg (
                frm TEXT,
                to0 TEXT,
                tos TEXT,
                subject TEXT,
                content TEXT,
                createDate timestamp
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS index_frm ON msg (frm)")
        cursor.execute("CREATE INDEX IF NOT EXISTS index_to0 ON msg (to0)")
        cursor.execute("CREATE INDEX IF NOT EXISTS index_date ON msg (createDate)")
        
        self.conn.commit()
    
    def store_message(self, message: Dict[str, Any]) -> None:
        """
        Store an email message.
        
        Args:
            message: Dictionary containing email data with keys:
                    'from', 'to', 'subject', 'content'
        """
        cursor = self.conn.cursor()
        
        # Extract first recipient for indexing
        to_list = message.get('to', [])
        first_to = to_list[0] if to_list else ''
        
        cursor.execute(
            "INSERT INTO msg VALUES (?, ?, ?, ?, ?, ?)",
            (
                message.get('from', ''),
                first_to,
                json.dumps(to_list),
                message.get('subject', ''),
                message.get('content', ''),
                datetime.datetime.now()
            )
        )
        self.conn.commit()
    
    def get_messages_from(self, sender: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get messages from a specific sender.
        
        Args:
            sender: Email address of the sender
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM msg WHERE frm = ? ORDER BY createDate DESC LIMIT ?",
            (sender, limit)
        )
        rows = cursor.fetchall()
        return self._transform_rows(rows)
    
    def get_messages_to(self, recipient: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get messages to a specific recipient.
        
        Args:
            recipient: Email address of the recipient
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM msg WHERE to0 = ? ORDER BY createDate DESC LIMIT ?",
            (recipient, limit)
        )
        rows = cursor.fetchall()
        return self._transform_rows(rows)
    
    def get_all_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all messages.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM msg ORDER BY createDate DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        return self._transform_rows(rows)
    
    def _transform_rows(self, rows: List[tuple]) -> List[Dict[str, Any]]:
        """
        Transform database rows to dictionaries.
        
        Args:
            rows: List of database row tuples
            
        Returns:
            List of message dictionaries
        """
        messages = []
        for row in rows:
            message = {
                "from": row[0],
                "to0": row[1],
                "to": json.loads(row[2]) if row[2] else [],
                "subject": row[3],
                "content": row[4],
                "time": row[5],
            }
            messages.append(message)
        return messages
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

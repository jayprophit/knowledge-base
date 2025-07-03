"""
Relational database module for the Knowledge Base Assistant.
Handles structured data like user accounts, settings, and system metadata.
Supports SQLite (for development) and PostgreSQL (for production).
"""

import logging
import os
import sqlite3
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class RelationalDBType(Enum):
    """Supported relational database types"""
    SQLITE = "sqlite"
    POSTGRES = "postgres"

class RelationalDB:
    """
    Relational database for structured data like user accounts and settings.
    Supports SQLite for local development and PostgreSQL for production.
    """
    def __init__(self,
                 db_type: Union[RelationalDBType, str] = RelationalDBType.SQLITE,
                 connection_string: Optional[str] = None,
                 auto_migrate: bool = True):
        """
        Initialize relational database connection.
        
        Args:
            db_type: Type of database (sqlite, postgres)
            connection_string: Connection string or path for the database
            auto_migrate: Whether to automatically create tables on startup
        """
        if isinstance(db_type, str):
            try:
                db_type = RelationalDBType(db_type.lower())
            except ValueError:
                logger.warning(f"Unknown DB type {db_type}, falling back to SQLITE")
                db_type = RelationalDBType.SQLITE
                
        self.db_type = db_type
        self.conn = None
        
        # Default local path for SQLite if not specified
        if connection_string is None and db_type == RelationalDBType.SQLITE:
            connection_string = os.path.join(os.path.dirname(__file__), 
                                           "../../data/relational_db/knowledge_assistant.db")
            # Ensure directory exists
            os.makedirs(os.path.dirname(connection_string), exist_ok=True)
            
        self.connection_string = connection_string
        self._connect()
        
        if auto_migrate:
            self._create_tables()
    
    def _connect(self):
        """Establish connection to the database"""
        try:
            if self.db_type == RelationalDBType.SQLITE:
                self._connect_sqlite()
            elif self.db_type == RelationalDBType.POSTGRES:
                self._connect_postgres()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
                
            logger.info(f"Connected to {self.db_type.value} database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _connect_sqlite(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.connection_string, 
                                       detect_types=sqlite3.PARSE_DECLTYPES)
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            logger.error(f"SQLite connection error: {e}")
            raise
    
    def _connect_postgres(self):
        """Connect to PostgreSQL database"""
        try:
            # Placeholder for actual PostgreSQL client initialization
            # import psycopg2
            # self.conn = psycopg2.connect(self.connection_string)
            logger.info("PostgreSQL client would be initialized here")
        except ImportError:
            logger.error("PostgreSQL client not installed. Run: pip install psycopg2-binary")
            raise
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.conn.cursor()
            
            # Users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
            ''')
            
            # Settings table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                user_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, key)
            )
            ''')
            
            # API keys table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                key TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
            ''')
            
            # Session tracking table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT
            )
            ''')
            
            self.conn.commit()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> Any:
        """
        Execute a raw SQL query with parameters.
        
        Args:
            query: SQL query string with placeholders
            params: Parameter values for the placeholders
            
        Returns:
            Query results
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            self.conn.rollback()
            raise
    
    def create_user(self, user_id: str, username: str, password_hash: str, 
                   email: Optional[str] = None) -> bool:
        """
        Create a new user.
        
        Args:
            user_id: Unique user identifier
            username: User's username
            password_hash: Hashed password (never store plaintext)
            email: Optional email address
            
        Returns:
            Success status
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''INSERT INTO users (id, username, email, password_hash, created_at) 
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, username, email, password_hash, datetime.now())
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            self.conn.rollback()
            return False
    
    def get_user(self, user_id: Optional[str] = None, 
                username: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get user by ID or username.
        
        Args:
            user_id: User ID to look up
            username: Username to look up
            
        Returns:
            User data dictionary or None if not found
        """
        try:
            cursor = self.conn.cursor()
            if user_id:
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            elif username:
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            else:
                logger.error("Either user_id or username must be provided")
                return None
                
            user = cursor.fetchone()
            if user:
                return dict(user)
            return None
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    def update_user(self, user_id: str, data: Dict[str, Any]) -> bool:
        """
        Update user data.
        
        Args:
            user_id: User ID to update
            data: Fields to update
            
        Returns:
            Success status
        """
        if not data:
            logger.warning("No data provided for update")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Build dynamic update query
            fields = []
            values = []
            for key, value in data.items():
                # Prevent updating ID
                if key == 'id':
                    continue
                fields.append(f"{key} = ?")
                values.append(value)
                
            if not fields:
                logger.warning("No valid fields to update")
                return False
                
            values.append(user_id)  # For WHERE clause
            
            query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, tuple(values))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            self.conn.rollback()
            return False
    
    def create_or_update_setting(self, user_id: str, key: str, value: str) -> bool:
        """
        Create or update a user setting.
        
        Args:
            user_id: User ID
            key: Setting key
            value: Setting value
            
        Returns:
            Success status
        """
        try:
            cursor = self.conn.cursor()
            
            # Check if setting exists
            cursor.execute('SELECT 1 FROM settings WHERE user_id = ? AND key = ?', 
                          (user_id, key))
            exists = cursor.fetchone() is not None
            
            if exists:
                cursor.execute(
                    '''UPDATE settings SET value = ?, updated_at = ? 
                       WHERE user_id = ? AND key = ?''',
                    (value, datetime.now(), user_id, key)
                )
            else:
                cursor.execute(
                    '''INSERT INTO settings (user_id, key, value, created_at, updated_at) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (user_id, key, value, datetime.now(), datetime.now())
                )
                
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save setting: {e}")
            self.conn.rollback()
            return False
    
    def get_settings(self, user_id: str) -> Dict[str, str]:
        """
        Get all settings for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary of settings
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT key, value FROM settings WHERE user_id = ?', (user_id,))
            return {row['key']: row['value'] for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"Failed to get settings: {e}")
            return {}
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    db = RelationalDB()
    
    # Create test user
    db.create_user("user123", "testuser", "hashed_password", "test@example.com")
    
    # Get user
    user = db.get_user(username="testuser")
    print(f"User: {user}")
    
    # Update user
    db.update_user("user123", {"last_login": datetime.now()})
    
    # Set settings
    db.create_or_update_setting("user123", "theme", "dark")
    db.create_or_update_setting("user123", "language", "en")
    
    # Get settings
    settings = db.get_settings("user123")
    print(f"Settings: {settings}")
    
    db.close()

"""
SQL utilities for the Knowledge Base Assistant.
Provides SQL query building, validation, and execution capabilities.
Supports both raw SQL and ORM-style operations with security features.
"""

import logging
import re
import sqlite3
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class SQLDialect(Enum):
    """Supported SQL dialects"""
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    MSSQL = "mssql"

class SQLQueryBuilder:
    """
    SQL query builder with security features.
    Helps construct parameterized SQL queries safely.
    """
    def __init__(self, dialect: SQLDialect = SQLDialect.SQLITE):
        """
        Initialize SQL query builder.
        
        Args:
            dialect: SQL dialect to use for query syntax
        """
        self.dialect = dialect
        self.reset()
    
    def reset(self):
        """Reset the query builder state"""
        self._select_parts = []
        self._from_parts = []
        self._where_parts = []
        self._order_parts = []
        self._group_parts = []
        self._having_parts = []
        self._limit_value = None
        self._offset_value = None
        self._parameters = {}
        self._param_counter = 0
        self._joins = []
        
        # Different dialects use different parameter styles
        if self.dialect == SQLDialect.SQLITE:
            self._param_style = "?"  # SQLite uses ? for parameters
        elif self.dialect in [SQLDialect.POSTGRES]:
            self._param_style = "%s"  # PostgreSQL uses %s
        elif self.dialect in [SQLDialect.MYSQL]:
            self._param_style = "%s"  # MySQL also uses %s
        elif self.dialect == SQLDialect.MSSQL:
            self._param_style = "@p"  # MSSQL uses @p1, @p2, etc.
    
    def select(self, *fields):
        """
        Add fields to SELECT clause
        
        Args:
            *fields: Fields to select
        
        Returns:
            self: For method chaining
        """
        for field in fields:
            self._select_parts.append(str(field))
        return self
    
    def from_table(self, table_name):
        """
        Add table to FROM clause
        
        Args:
            table_name: Table name
        
        Returns:
            self: For method chaining
        """
        self._from_parts.append(str(table_name))
        return self
    
    def where(self, condition, **params):
        """
        Add condition to WHERE clause
        
        Args:
            condition: WHERE condition with placeholders
            **params: Parameter values
        
        Returns:
            self: For method chaining
        """
        # Replace named placeholders with dialect-specific placeholders
        if self.dialect == SQLDialect.MSSQL:
            # For MSSQL, we need to replace :name with @pN
            for name, value in params.items():
                placeholder = f":{name}"
                param_name = f"p{self._param_counter}"
                self._param_counter += 1
                condition = condition.replace(placeholder, f"@{param_name}")
                self._parameters[param_name] = value
        else:
            # For other DBs, just add parameters
            for name, value in params.items():
                self._parameters[name] = value
        
        self._where_parts.append(condition)
        return self
    
    def order_by(self, *fields):
        """
        Add fields to ORDER BY clause
        
        Args:
            *fields: Fields to order by
        
        Returns:
            self: For method chaining
        """
        for field in fields:
            self._order_parts.append(str(field))
        return self
    
    def group_by(self, *fields):
        """
        Add fields to GROUP BY clause
        
        Args:
            *fields: Fields to group by
        
        Returns:
            self: For method chaining
        """
        for field in fields:
            self._group_parts.append(str(field))
        return self
    
    def having(self, condition, **params):
        """
        Add condition to HAVING clause
        
        Args:
            condition: HAVING condition with placeholders
            **params: Parameter values
        
        Returns:
            self: For method chaining
        """
        # Handle parameters similar to where()
        for name, value in params.items():
            self._parameters[name] = value
        
        self._having_parts.append(condition)
        return self
    
    def limit(self, value):
        """
        Set LIMIT clause
        
        Args:
            value: Limit value
        
        Returns:
            self: For method chaining
        """
        self._limit_value = int(value)
        return self
    
    def offset(self, value):
        """
        Set OFFSET clause
        
        Args:
            value: Offset value
        
        Returns:
            self: For method chaining
        """
        self._offset_value = int(value)
        return self
    
    def join(self, table, condition, join_type="INNER"):
        """
        Add JOIN clause
        
        Args:
            table: Table to join
            condition: Join condition
            join_type: Type of join (INNER, LEFT, RIGHT, etc.)
        
        Returns:
            self: For method chaining
        """
        self._joins.append({
            "table": str(table),
            "condition": condition,
            "type": join_type
        })
        return self
    
    def build(self) -> Tuple[str, Dict[str, Any]]:
        """
        Build the SQL query and parameters
        
        Returns:
            Tuple[str, Dict[str, Any]]: SQL query string and parameters dict
        """
        parts = []
        
        # SELECT
        select_clause = "SELECT "
        if not self._select_parts:
            select_clause += "*"
        else:
            select_clause += ", ".join(self._select_parts)
        parts.append(select_clause)
        
        # FROM
        if self._from_parts:
            parts.append(f"FROM {', '.join(self._from_parts)}")
        
        # JOINs
        for join in self._joins:
            parts.append(f"{join['type']} JOIN {join['table']} ON {join['condition']}")
        
        # WHERE
        if self._where_parts:
            parts.append(f"WHERE {' AND '.join(self._where_parts)}")
        
        # GROUP BY
        if self._group_parts:
            parts.append(f"GROUP BY {', '.join(self._group_parts)}")
        
        # HAVING
        if self._having_parts:
            parts.append(f"HAVING {' AND '.join(self._having_parts)}")
        
        # ORDER BY
        if self._order_parts:
            parts.append(f"ORDER BY {', '.join(self._order_parts)}")
        
        # LIMIT
        if self._limit_value is not None:
            parts.append(f"LIMIT {self._limit_value}")
        
        # OFFSET
        if self._offset_value is not None:
            parts.append(f"OFFSET {self._offset_value}")
        
        sql = " ".join(parts)
        return sql, self._parameters

class SQLValidator:
    """
    SQL validator for security and syntax checking.
    Helps prevent SQL injection and validate query structure.
    """
    # Blacklisted SQL commands that can modify data or schema
    DANGEROUS_COMMANDS = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'TRUNCATE',
        'CREATE', 'GRANT', 'REVOKE', 'ADD', 'SET', 'INTO', 'MERGE'
    ]
    
    @staticmethod
    def is_safe_query(query: str) -> bool:
        """
        Check if a query is safe (read-only)
        
        Args:
            query: SQL query to validate
        
        Returns:
            bool: True if query is read-only
        """
        # Convert to uppercase for case-insensitive matching
        upper_query = query.upper()
        
        # Check for dangerous commands
        for command in SQLValidator.DANGEROUS_COMMANDS:
            # Use word boundary to match whole words
            pattern = r'\b' + command + r'\b'
            if re.search(pattern, upper_query):
                return False
        
        return True
    
    @staticmethod
    def validate_syntax(query: str, dialect: SQLDialect = SQLDialect.SQLITE) -> Tuple[bool, str]:
        """
        Validate SQL syntax
        
        Args:
            query: SQL query to validate
            dialect: SQL dialect to use for validation
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if dialect == SQLDialect.SQLITE:
            try:
                conn = sqlite3.connect(':memory:')
                conn.execute("EXPLAIN " + query)
                conn.close()
                return True, ""
            except sqlite3.Error as e:
                return False, str(e)
        else:
            # For other dialects, we'd need specific validators
            # This is a placeholder for extensibility
            logger.warning(f"Syntax validation for {dialect.value} not implemented")
            return True, "Validation not implemented for this dialect"
    
    @staticmethod
    def sanitize_identifier(identifier: str) -> str:
        """
        Sanitize a SQL identifier (table or column name)
        
        Args:
            identifier: SQL identifier to sanitize
        
        Returns:
            str: Sanitized identifier
        """
        # Remove SQL special chars and allow only alphanumeric and underscores
        return re.sub(r'[^\w]', '', identifier)

class SQLExecutor:
    """
    SQL executor for running queries against databases.
    Handles connections, transactions, and result formatting.
    """
    def __init__(self, connection):
        """
        Initialize SQL executor with a database connection
        
        Args:
            connection: Database connection object
        """
        self.connection = connection
    
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as a list of dictionaries
        
        Args:
            query: SQL query string
            parameters: Query parameters
            
        Returns:
            List[Dict[str, Any]]: Query results as list of row dictionaries
        """
        try:
            # Validate query for security
            if not SQLValidator.is_safe_query(query):
                raise ValueError("Query contains unsafe operations")
            
            cursor = self.connection.cursor()
            
            # Execute with parameters if provided
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            # Get column names
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Convert rows to dictionaries
            results = []
            for row in cursor.fetchall():
                results.append({column_names[i]: row[i] for i in range(len(row))})
            
            return results
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            raise

class JSONSQLFormatter:
    """
    Format SQL results as JSON with type handling
    """
    @staticmethod
    def format_results(results: List[Dict[str, Any]]) -> str:
        """
        Format SQL results as JSON string
        
        Args:
            results: Query results
            
        Returns:
            str: JSON formatted results
        """
        # Custom encoder to handle dates and other special types
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        return json.dumps(results, cls=CustomJSONEncoder, indent=2)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    # Build a query
    builder = SQLQueryBuilder(dialect=SQLDialect.SQLITE)
    query, params = builder.select("users.username", "settings.value") \
        .from_table("users") \
        .join("settings", "users.id = settings.user_id") \
        .where("users.is_active = :active", active=True) \
        .where("settings.key = :key", key="theme") \
        .order_by("users.username") \
        .limit(10) \
        .build()
    
    print(f"Generated SQL: {query}")
    print(f"Parameters: {params}")
    
    # Validate a query
    is_safe = SQLValidator.is_safe_query("SELECT * FROM users WHERE username = 'test'")
    print(f"Is safe query: {is_safe}")
    
    is_valid, error = SQLValidator.validate_syntax("SELECT * FROM users WHERE username = 'test'")
    print(f"Is valid syntax: {is_valid}, Error: {error}")

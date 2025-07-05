"""
SQL Query Builder for Knowledge Base Assistant
Builds safe, parameterized SQL queries for multiple dialects.
"""
from typing import Dict, Any, List, Tuple, Optional

class SQLBuilder:
    """
    Utility for building parameterized SQL queries (select, insert, update, delete, join)
    """
    def select(self, table: str, columns: List[str], where: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> Tuple[str, List[Any]]:
        query = f"SELECT {', '.join(columns)} FROM {table}"
        params = []
        if where:
            conditions = [f"{k} = ?" for k in where.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params.extend(where.values())
        if limit:
            query += f" LIMIT {limit}"
        return query, params

    def insert(self, table: str, data: Dict[str, Any]) -> Tuple[str, List[Any]]:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return query, list(data.values())

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> Tuple[str, List[Any]]:
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = list(data.values()) + list(where.values())
        return query, params

    def delete(self, table: str, where: Dict[str, Any]) -> Tuple[str, List[Any]]:
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        params = list(where.values())
        return query, params

    def join(self, left: str, right: str, left_key: str, right_key: str, columns: List[str]) -> str:
        cols = ', '.join(columns)
        query = f"SELECT {cols} FROM {left} JOIN {right} ON {left}.{left_key} = {right}.{right_key}"
        return query

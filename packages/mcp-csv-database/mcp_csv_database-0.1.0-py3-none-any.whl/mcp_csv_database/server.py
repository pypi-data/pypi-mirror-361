#!/usr/bin/env python3
"""
MCP Server for CSV File Management
Loads CSV files from a folder into a temporary SQLite database and provides SQL query capabilities.
"""

import os
import sqlite3
import pandas as pd
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
import asyncio
import json

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.prompts import base

# Initialize the MCP server
mcp = FastMCP("CSV Database Server")

# Global variables to store database connection and loaded tables
_db_connection: Optional[sqlite3.Connection] = None
_loaded_tables: Dict[str, str] = {}  # table_name -> csv_file_path
_db_path: Optional[str] = None


@mcp.tool()
def get_database_schema() -> str:
    """Get the current database schema showing all loaded tables and their structure"""
    if not _db_connection:
        return "No database loaded. Use load_csv_folder tool first."
    
    try:
        cursor = _db_connection.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            return "Database is empty. No tables loaded."
        
        schema_info = []
        for (table_name,) in tables:
            schema_info.append(f"\n=== Table: {table_name} ===")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            schema_info.append("Columns:")
            for col in columns:
                col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
                pk_indicator = " (PRIMARY KEY)" if pk else ""
                null_indicator = " NOT NULL" if not_null else ""
                default_indicator = f" DEFAULT {default}" if default else ""
                schema_info.append(f"  - {col_name}: {col_type}{pk_indicator}{null_indicator}{default_indicator}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            schema_info.append(f"Row count: {count}")
            
            # Show sample data (first 3 rows)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_rows = cursor.fetchall()
            if sample_rows:
                schema_info.append("Sample data:")
                column_names = [desc[0] for desc in cursor.description]
                for row in sample_rows:
                    row_dict = dict(zip(column_names, row))
                    schema_info.append(f"  {row_dict}")
        
        return "\n".join(schema_info)
        
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"


@mcp.tool()
def list_loaded_tables() -> str:
    """List all currently loaded tables with their source CSV files"""
    if not _loaded_tables:
        return "No tables loaded."
    
    table_list = []
    for table_name, csv_path in _loaded_tables.items():
        table_list.append(f"- {table_name} (from {csv_path})")
    
    return "Loaded tables:\n" + "\n".join(table_list)


@mcp.tool()
def load_csv_folder(folder_path: str, table_prefix: str = "") -> str:
    """
    Load all CSV files from a folder into a temporary SQLite database.
    
    Args:
        folder_path: Path to folder containing CSV files
        table_prefix: Optional prefix for table names
    
    Returns:
        Status message with details of loaded files
    """
    global _db_connection, _loaded_tables, _db_path
    
    try:
        # Validate folder path
        folder = Path(folder_path)
        if not folder.exists():
            return f"Error: Folder '{folder_path}' does not exist."
        
        if not folder.is_dir():
            return f"Error: '{folder_path}' is not a directory."
        
        # Find CSV files
        csv_files = list(folder.glob("*.csv"))
        if not csv_files:
            return f"No CSV files found in '{folder_path}'."
        
        # Create temporary database
        if _db_connection:
            _db_connection.close()
        
        # Create a temporary file for the database
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        _db_path = temp_db.name
        temp_db.close()
        
        _db_connection = sqlite3.connect(_db_path)
        _loaded_tables = {}
        
        results = []
        successful_loads = 0
        
        for csv_file in csv_files:
            try:
                # Generate table name
                table_name = table_prefix + csv_file.stem.replace("-", "_").replace(" ", "_")
                
                # Load CSV into pandas DataFrame - try different separators
                df = None
                separators = [';', ',', '\t']
                for sep in separators:
                    try:
                        df = pd.read_csv(csv_file, sep=sep, encoding='utf-8')
                        # Check if we got meaningful columns (more than 1 column usually indicates correct separator)
                        if len(df.columns) > 1:
                            break
                    except:
                        continue
                
                if df is None:
                    # Fallback to default pandas behavior
                    df = pd.read_csv(csv_file)
                
                # Load DataFrame into SQLite
                df.to_sql(table_name, _db_connection, index=False, if_exists='replace')
                
                _loaded_tables[table_name] = str(csv_file)
                results.append(f"✓ Loaded {csv_file.name} -> table '{table_name}' ({len(df)} rows, {len(df.columns)} columns)")
                successful_loads += 1
                
            except Exception as e:
                results.append(f"✗ Failed to load {csv_file.name}: {str(e)}")
        
        summary = f"Loaded {successful_loads}/{len(csv_files)} CSV files into temporary database.\n"
        summary += f"Database path: {_db_path}\n\n"
        summary += "\n".join(results)
        
        return summary
        
    except Exception as e:
        return f"Error loading CSV folder: {str(e)}"


@mcp.tool()
def execute_sql_query(query: str, limit: int = 100) -> str:
    """
    Execute any SQL query on the loaded database.
    
    Args:
        query: Any SQL query to execute (SELECT, INSERT, UPDATE, DELETE, CREATE, etc.)
        limit: Maximum number of rows to return for SELECT queries (default: 100)
    
    Returns:
        Query results formatted as JSON or execution status
    """
    if not _db_connection:
        return "Error: No database loaded. Use load_csv_folder tool first."
    
    try:
        cursor = _db_connection.cursor()
        query_upper = query.strip().upper()
        
        # Execute the query
        cursor.execute(query)
        
        # Handle different types of queries
        if query_upper.startswith('SELECT'):
            # For SELECT queries, return data
            column_names = [description[0] for description in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            if not rows:
                return "Query executed successfully. No results returned."
            
            # Apply limit for SELECT queries if not already present
            if 'LIMIT' not in query_upper and len(rows) > limit:
                rows = rows[:limit]
                limited = True
            else:
                limited = False
            
            # Convert to list of dictionaries
            results = []
            for row in rows:
                row_dict = dict(zip(column_names, row))
                results.append(row_dict)
            
            # Format output
            output = {
                "query": query,
                "query_type": "SELECT",
                "row_count": len(results),
                "limited": limited,
                "columns": column_names,
                "data": results
            }
            
            return json.dumps(output, indent=2, default=str)
            
        else:
            # For non-SELECT queries (INSERT, UPDATE, DELETE, CREATE, etc.)
            _db_connection.commit()  # Commit changes
            rows_affected = cursor.rowcount
            
            # Determine query type
            query_type = query_upper.split()[0] if query_upper.split() else "UNKNOWN"
            
            output = {
                "query": query,
                "query_type": query_type,
                "rows_affected": rows_affected,
                "status": "success",
                "message": f"{query_type} query executed successfully"
            }
            
            return json.dumps(output, indent=2, default=str)
        
    except Exception as e:
        return f"Error executing query: {str(e)}"


@mcp.tool()
def get_table_info(table_name: str) -> str:
    """
    Get detailed information about a specific table.
    
    Args:
        table_name: Name of the table to inspect
    
    Returns:
        Detailed table information including schema and sample data
    """
    if not _db_connection:
        return "Error: No database loaded. Use load_csv_folder tool first."
    
    try:
        cursor = _db_connection.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            available_tables = list(_loaded_tables.keys())
            return f"Table '{table_name}' not found. Available tables: {available_tables}"
        
        info = []
        info.append(f"=== Table: {table_name} ===")
        
        # Source file info
        if table_name in _loaded_tables:
            info.append(f"Source CSV: {_loaded_tables[table_name]}")
        
        # Column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        info.append(f"\nColumns ({len(columns)}):")
        for col in columns:
            col_name, col_type = col[1], col[2]
            info.append(f"  - {col_name}: {col_type}")
        
        # Row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        info.append(f"\nTotal rows: {count}")
        
        # Sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        sample_rows = cursor.fetchall()
        if sample_rows:
            info.append("\nSample data (first 5 rows):")
            column_names = [desc[0] for desc in cursor.description]
            for i, row in enumerate(sample_rows, 1):
                row_dict = dict(zip(column_names, row))
                info.append(f"  Row {i}: {row_dict}")
        
        return "\n".join(info)
        
    except Exception as e:
        return f"Error getting table info: {str(e)}"


@mcp.tool()
def create_index(table_name: str, column_name: str, index_name: str = "") -> str:
    """
    Create an index on a table column for better query performance.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column to index
        index_name: Optional custom index name
    
    Returns:
        Status message
    """
    if not _db_connection:
        return "Error: No database loaded. Use load_csv_folder tool first."
    
    try:
        if not index_name:
            index_name = f"idx_{table_name}_{column_name}"
        
        # Sanitize column name if it contains spaces or special characters
        if ' ' in column_name or any(char in column_name for char in ['-', '.', '(', ')']):
            column_ref = f'"{column_name}"'
        else:
            column_ref = column_name
        
        query = f'CREATE INDEX IF NOT EXISTS "{index_name}" ON "{table_name}" ({column_ref})'
        
        cursor = _db_connection.cursor()
        cursor.execute(query)
        _db_connection.commit()
        
        return f"Index '{index_name}' created successfully on {table_name}.{column_name}"
        
    except Exception as e:
        return f"Error creating index: {str(e)}"


@mcp.tool()
def backup_database(backup_path: str) -> str:
    """
    Create a backup of the current database to a file.
    
    Args:
        backup_path: Path where to save the backup file
    
    Returns:
        Status message
    """
    if not _db_connection:
        return "Error: No database loaded. Use load_csv_folder tool first."
    
    try:
        backup_path = Path(backup_path)
        
        # Create backup using SQLite backup
        backup_conn = sqlite3.connect(backup_path)
        _db_connection.backup(backup_conn)
        backup_conn.close()
        
        return f"Database backed up successfully to: {backup_path}"
        
    except Exception as e:
        return f"Error creating backup: {str(e)}"


@mcp.tool()
def export_table_to_csv(table_name: str, output_path: str, include_header: bool = True) -> str:
    """
    Export a table to a CSV file.
    
    Args:
        table_name: Name of the table to export
        output_path: Path for the output CSV file
        include_header: Whether to include column headers
    
    Returns:
        Status message
    """
    if not _db_connection:
        return "Error: No database loaded. Use load_csv_folder tool first."
    
    try:
        # Read table into pandas DataFrame
        df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', _db_connection)
        
        # Export to CSV
        df.to_csv(output_path, index=False, header=include_header, sep=';', encoding='utf-8')
        
        return f"Table '{table_name}' exported successfully to: {output_path} ({len(df)} rows)"
        
    except Exception as e:
        return f"Error exporting table: {str(e)}"


@mcp.tool()
def get_query_plan(query: str) -> str:
    """
    Get the execution plan for a query to understand performance.
    
    Args:
        query: SQL query to analyze
    
    Returns:
        Query execution plan
    """
    if not _db_connection:
        return "Error: No database loaded. Use load_csv_folder tool first."
    
    try:
        cursor = _db_connection.cursor()
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        cursor.execute(explain_query)
        
        plan_rows = cursor.fetchall()
        
        if not plan_rows:
            return "No execution plan available."
        
        plan_info = ["Query Execution Plan:", "=" * 30]
        for row in plan_rows:
            plan_info.append(f"Step {row[0]}: {row[3]}")
        
        return "\n".join(plan_info)
        
    except Exception as e:
        return f"Error getting query plan: {str(e)}"


@mcp.tool()
def clear_database() -> str:
    """
    Clear the temporary database and remove all loaded tables.
    
    Returns:
        Status message
    """
    global _db_connection, _loaded_tables, _db_path
    
    try:
        if _db_connection:
            _db_connection.close()
            _db_connection = None
        
        if _db_path and os.path.exists(_db_path):
            os.unlink(_db_path)
            _db_path = None
        
        table_count = len(_loaded_tables)
        _loaded_tables = {}
        
        return f"Database cleared. Removed {table_count} tables."
        
    except Exception as e:
        return f"Error clearing database: {str(e)}"


@mcp.prompt()
def analyze_data_prompt(table_name: str, analysis_type: str = "summary") -> str:
    """
    Generate a prompt for analyzing data in a specific table.
    
    Args:
        table_name: Name of the table to analyze
        analysis_type: Type of analysis (summary, trends, insights, etc.)
    """
    if table_name not in _loaded_tables:
        available_tables = list(_loaded_tables.keys())
        return f"Table '{table_name}' not found. Available tables: {available_tables}"
    
    return f"""Please analyze the data in table '{table_name}' and provide a {analysis_type}.

Available analysis types:
- summary: Basic statistics and data overview
- trends: Identify patterns and trends in the data
- insights: Generate business insights from the data
- quality: Assess data quality and identify issues

Use the execute_sql_query tool to explore the data and provide your analysis."""


# Cleanup function to be called on server shutdown
def cleanup():
    """Cleanup function to close database connection and remove temporary files"""
    global _db_connection, _db_path
    
    if _db_connection:
        _db_connection.close()
    
    if _db_path and os.path.exists(_db_path):
        try:
            os.unlink(_db_path)
        except:
            pass  # Ignore errors during cleanup


def main():
    """Main entry point for the MCP server"""
    import argparse
    import atexit
    atexit.register(cleanup)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="CSV Database MCP Server")
    parser.add_argument(
        "--csv-folder", 
        type=str, 
        help="Path to folder containing CSV files to auto-load on startup"
    )
    parser.add_argument(
        "--table-prefix", 
        type=str, 
        default="", 
        help="Optional prefix for table names"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport type (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port for HTTP transport (default: 3000)"
    )
    
    args = parser.parse_args()
    
    print("🗃️  CSV Database MCP Server")
    
    # Auto-load CSV files if folder specified
    if args.csv_folder:
        print(f"📁 Auto-loading CSV files from: {args.csv_folder}")
        result = load_csv_folder(args.csv_folder, args.table_prefix)
        print(result)
        print()
    
    print("Ready to load CSV files and execute SQL queries!")
    print("\nAvailable tools:")
    print("- load_csv_folder: Load CSV files from a folder")
    print("- execute_sql_query: Run SQL queries on loaded data")
    print("- get_table_info: Get detailed table information")
    print("- clear_database: Clear all loaded data")
    print("- get_database_schema: View database schema")
    print("- list_loaded_tables: List loaded tables")
    
    # Run the server with specified transport
    if args.transport == "stdio":
        mcp.run()
    elif args.transport == "sse":
        mcp.run(transport="sse", port=args.port)
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", port=args.port)


# Main execution
if __name__ == "__main__":
    main()
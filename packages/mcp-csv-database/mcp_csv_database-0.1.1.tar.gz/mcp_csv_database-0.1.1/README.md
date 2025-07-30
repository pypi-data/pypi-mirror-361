# MCP CSV Database Server

A Model Context Protocol (MCP) server that provides tools for loading CSV files into a temporary SQLite database and executing SQL queries on the data.

## Features

- **Load CSV files**: Automatically detect CSV separators and load multiple files from a folder
- **SQL queries**: Execute any SQL query on loaded data with result formatting
- **Schema inspection**: View database schema and table structures
- **Data analysis**: Built-in tools for data exploration and analysis
- **Export capabilities**: Export query results or tables back to CSV
- **Performance tools**: Create indexes and analyze query execution plans

## Installation

### From PyPI

```bash
pip install mcp-csv-database
```

### From source

```bash
git clone https://github.com/Lasitha-Jayawardana/mcp-csv-database.git
cd mcp-csv-database
pip install -e .
```

## Usage

### Command Line

Start the server with stdio transport:

```bash
mcp-csv-database
```

Or auto-load CSV files from a folder:

```bash
mcp-csv-database --csv-folder /path/to/csv/files
```

### Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "csv-database": {
      "command": "mcp-csv-database",
      "args": ["--csv-folder", "/path/to/your/csv/files"]
    }
  }
}
```

## Available Tools

### Data Loading
- `load_csv_folder(folder_path, table_prefix="")` - Load all CSV files from a folder
- `list_loaded_tables()` - List currently loaded tables
- `clear_database()` - Clear all loaded data

### Data Querying
- `execute_sql_query(query, limit=100)` - Execute SQL queries with automatic result formatting
- `get_database_schema()` - View complete database schema
- `get_table_info(table_name)` - Get detailed information about a specific table

### Data Analysis
- `get_query_plan(query)` - Analyze query execution plans
- `create_index(table_name, column_name, index_name="")` - Create indexes for better performance

### Data Export
- `export_table_to_csv(table_name, output_path, include_header=True)` - Export tables to CSV
- `backup_database(backup_path)` - Create database backups

## Examples

### Basic Usage

```python
# Load CSV files
result = load_csv_folder("/path/to/csv/files")

# View what's loaded
schema = get_database_schema()

# Query the data
result = execute_sql_query("SELECT * FROM my_table LIMIT 10")

# Export results
export_table_to_csv("my_table", "/path/to/output.csv")
```

### Data Analysis

```python
# Get table information
info = get_table_info("sales_data")

# Analyze data
result = execute_sql_query("""
    SELECT 
        category,
        COUNT(*) as count,
        AVG(price) as avg_price,
        SUM(quantity) as total_quantity
    FROM sales_data 
    GROUP BY category
    ORDER BY total_quantity DESC
""")

# Create index for better performance
create_index("sales_data", "category")
```

## Transport Options

The server supports multiple transport methods:

- `stdio` (default): Standard input/output
- `sse`: Server-sent events
- `streamable-http`: HTTP streaming

```bash
# SSE transport
mcp-csv-database --transport sse --port 8080

# HTTP transport  
mcp-csv-database --transport streamable-http --port 8080
```

## Requirements

- Python 3.8+
- pandas
- sqlite3 (built-in)
- mcp

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0
- Initial release
- Basic CSV loading and SQL querying
- Schema inspection tools
- Data export capabilities
- Multiple transport support
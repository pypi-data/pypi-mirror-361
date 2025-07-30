# [Query.Farm](https://query.farm) SQL Manipulation

A Python library for intelligent SQL predicate manipulation using [SQLGlot](https://sqlglot.org)

### Column Filtering with Complex Expressions

```python
import sqlglot
from query_farm_sql_manipulation import transforms

sql = '''
SELECT * FROM users
WHERE age > 18
  AND (status = 'active' OR role = 'admin')
  AND department IN ('engineering', 'sales')
'''

# Parse the statement first
statement = sqlglot.parse_one(sql, dialect="duckdb")

# Only keep predicates involving 'age' and 'role'
allowed_columns = {'age', 'role'}

result = transforms.filter_column_references(
    statement=statement,
    selector=lambda col: col.name in allowed_columns,
)

# Result: SELECT * FROM users WHERE age > 18 AND role = 'admin'
print(result.sql())
```

## Features

- **Predicate Removal**: Safely remove specific predicates from complex `SQL WHERE` clauses while preserving logical structure
- **Column Filtering**: Filter SQL statements to only include predicates referencing allowed columns
- **Intelligent Logic Handling**: Properly handles `AND/OR` logic, nested expressions, `CASE` statements, and parentheses
- **SQLGlot Integration**: Built on top of [SQLGlot](https://sqlglot.com/sqlglot.html) for robust SQL parsing and manipulation
- **Multiple Dialect Support**: Works with various SQL dialects (default: DuckDB)

## Installation

```bash
pip install query-farm-sql-manipulation
```

## Requirements

- Python >= 3.12
- SQLGlot >= 26.33.0

## Quick Start

### Basic Predicate Removal

```python
import sqlglot
from query_farm_sql_manipulation import transforms

# Parse a SQL statement
sql = 'SELECT * FROM data WHERE x = 1 AND y = 2'
statement = sqlglot.parse_one(sql, dialect="duckdb")

# Find the predicate you want to remove
predicates = list(statement.find_all(sqlglot.expressions.Predicate))
target_predicate = predicates[0]  # x = 1

# Remove the predicate
transforms.remove_expression_part(target_predicate)

# Result: SELECT * FROM data WHERE y = 2
print(statement.sql())
```

### Column-Name Based Filtering

```python
import sqlglot
from query_farm_sql_manipulation import transforms

# Parse SQL statement first
sql = 'SELECT * FROM data WHERE color = "red" AND size > 10 AND type = "car"'
statement = sqlglot.parse_one(sql, dialect="duckdb")

# Filter to only include predicates with allowed columns
allowed_columns = {"color", "type"}

filtered = transforms.filter_column_references(
    statement=statement,
    selector=lambda col: col.name in allowed_columns,
)

# Result: SELECT * FROM data WHERE color = "red" AND type = "car"
print(filtered.sql())
```

## API Reference

### `remove_expression_part(child: sqlglot.Expression) -> None`

Removes the specified SQLGlot expression from its parent, respecting logical structure.

**Parameters:**
- `child`: The SQLGlot expression to remove

**Raises:**
- `ValueError`: If the expression cannot be safely removed

**Supported Parent Types:**
- `AND`/`OR` expressions: Replaces parent with the remaining operand
- `WHERE` clauses: Removes the entire WHERE clause if it becomes empty
- `Parentheses`: Recursively removes the parent
- `NOT` expressions: Removes the entire NOT expression
- `CASE` statements: Removes conditional branches

### `filter_column_references(*, statement: sqlglot.Expression, selector: Callable[[sqlglot.expressions.Column], bool]) -> sqlglot.Expression`

Filters a SQL statement to remove predicates containing columns that don't match the selector criteria.

**Parameters:**
- `statement`: The SQLGlot expression to filter
- `selector`: A callable that takes a Column and returns True if it should be preserved, False if it should be removed

**Returns:**
- Filtered SQLGlot expression with non-matching columns removed

**Raises:**
- `ValueError`: If a column can't be cleanly removed due to interactions with allowed columns

### `where_clause_contents(statement: sqlglot.expressions.Expression) -> sqlglot.expressions.Expression | None`

Extracts the contents of the WHERE clause from a SQLGlot expression.

**Parameters:**
- `statement`: The SQLGlot expression to extract from

**Returns:**
- The contents of the WHERE clause, or None if no WHERE clause exists

### `filter_predicates_with_right_side_column_references(statement: sqlglot.expressions.Expression) -> sqlglot.Expression`

Filters out predicates that have column references on the right side of comparisons.

**Parameters:**
- `statement`: The SQLGlot expression to filter

**Returns:**
- Filtered SQLGlot expression with right-side column reference predicates removed

## Examples

### Complex Logic Handling

The library intelligently handles complex logical expressions:

```python
# Original: (x = 1 AND y = 2) OR z = 3
# Remove y = 2: x = 1 OR z = 3

# Original: NOT (x = 1 AND y = 2)
# Remove x = 1: NOT y = 2 (which becomes y <> 2)

# Original: CASE WHEN x = 1 THEN 'yes' WHEN x = 2 THEN 'maybe' ELSE 'no' END
# Remove x = 1: CASE WHEN x = 2 THEN 'maybe' ELSE 'no' END
```

### Column Filtering with Complex Expressions

```python
sql = '''
SELECT * FROM users
WHERE age > 18
  AND (status = 'active' OR role = 'admin')
  AND department IN ('engineering', 'sales')
'''

# Only keep predicates involving 'age' and 'role'
allowed_columns = {'age', 'role'}

result = transforms.filter_column_references_statement(
    sql=sql,
    allowed_column_names=allowed_columns
)

# Result: SELECT * FROM users WHERE age > 18 AND role = 'admin'
```

### Error Handling

The library will raise `ValueError` when predicates cannot be safely removed:

```python
import sqlglot
from query_farm_sql_manipulation import transforms

# This will raise ValueError because x = 1 is part of a larger expression
sql = "SELECT * FROM data WHERE result = (x = 1)"
statement = sqlglot.parse_one(sql, dialect="duckdb")

# Cannot remove x = 1 because it's used as a value, not a predicate
# This would raise ValueError if attempted
```

## Supported SQL Constructs

- **Logical Operators**: `AND`, `OR`, `NOT`
- **Comparison Operators**: `=`, `<>`, `<`, `>`, `<=`, `>=`, `LIKE`, `IN`, `IS NULL`, etc.
- **Complex Expressions**: `CASE` statements, subqueries, function calls
- **Nested Logic**: Parentheses and nested boolean expressions
- **Multiple Dialects**: DuckDB, PostgreSQL, MySQL, SQLite, and more via SQLGlot

## Testing

Run the test suite:

```bash
pytest src/query_farm_sql_manipulation/test_transforms.py
```

The test suite includes comprehensive examples of:
- Basic predicate removal scenarios
- Complex logical expression handling
- Error cases and edge conditions
- Column filtering with various SQL constructs

## Contributing

This project uses:
- **Rye** for dependency management
- **pytest** for testing
- **mypy** for type checking
- **ruff** for linting


## Author

This Python module was created by [Query.Farm](https://query.farm).

# License

MIT Licensed.


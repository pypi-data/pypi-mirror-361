"""
PostgreSQL dialect implementation for FHIR4DS.

This module provides PostgreSQL-specific functionality for FHIR data storage,
optimized for JSONB operations and performance.
"""

import json
import logging
from typing import Dict, List, Any, Optional

from .base import DatabaseDialect

# Optional import for PostgreSQL
try:
    import psycopg2
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

logger = logging.getLogger(__name__)


class PostgreSQLDialect(DatabaseDialect):
    """PostgreSQL implementation of the database dialect"""
    
    def __init__(self, conn_str: str):
        super().__init__()  # Initialize base class
        
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("psycopg2 is required but not installed. Install with: pip install psycopg2-binary")
        
        # PostgreSQL-specific settings
        self.name = "POSTGRESQL"
        self.supports_jsonb = True
        self.supports_json_functions = True
        self.json_type = "JSONB"
        # Function mappings for PostgreSQL - now properly integrated with dialect-aware generation
        self.json_extract_function = "jsonb_extract_path"
        self.json_extract_string_function = "jsonb_extract_path_text"
        self.json_array_function = "jsonb_build_array"
        self.json_object_function = "jsonb_build_object"
        self.json_type_function = "jsonb_typeof"
        self.json_array_length_function = "jsonb_array_length"
        self.json_each_function = "jsonb_each"
        self.array_agg_function = "array_agg"
        self.string_agg_function = "string_agg"
        self.regex_function = "substring"
        self.cast_syntax = "::"
        self.quote_char = '"'
        
        # PostgreSQL-specific JSONB functions
        self.jsonb_path_query_function = "jsonb_path_query"
        self.jsonb_path_query_first_function = "jsonb_path_query_first"
        self.jsonb_path_exists_function = "jsonb_path_exists"
        self.jsonb_array_elements_function = "jsonb_array_elements"
        self.jsonb_array_elements_text_function = "jsonb_array_elements_text"
        
        self.connection = psycopg2.connect(conn_str)
        self.connection.autocommit = True  # Enable autocommit to avoid transaction issues
        logger.info("Initialized PostgreSQL dialect")
    
    def get_connection(self) -> Any:
        return self.connection
    
    def execute_sql(self, sql: str, view_def: Optional[Dict] = None) -> 'QueryResult':
        """Execute SQL and return wrapped results"""
        # Apply PostgreSQL-specific transformations to convert generic functions
        translated_sql = self.translate_sql(sql)
        logger.debug(f"Executing PostgreSQL SQL: {translated_sql}")
        
        # Import locally to avoid circular imports
        from .. import datastore
        from ..datastore import QueryResult
        return QueryResult(self, translated_sql, view_def)
    
    def execute_query(self, sql: str) -> Any:
        """Execute a query and return raw results"""
        # Apply PostgreSQL-specific transformations to convert generic functions
        translated_sql = self.translate_sql(sql)
        logger.debug(f"Executing PostgreSQL SQL: {translated_sql}")
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(translated_sql)
            # Store the cursor description for later retrieval
            self._last_cursor_description = cursor.description
            return cursor.fetchall()
        except Exception as e:
            # With autocommit=True, no need to rollback
            logger.error(f"PostgreSQL execution failed: {e}\nSQL: {sql}")
            raise e
    
    def get_query_description(self, connection: Any) -> Any:
        """Get column descriptions from last executed query"""
        return getattr(self, '_last_cursor_description', None)
    
    def create_fhir_table(self, table_name: str, json_col: str) -> None:
        """Create FHIR resources table optimized for PostgreSQL"""
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        cursor.execute(f"""
            CREATE TABLE {table_name} (
                id SERIAL PRIMARY KEY,
                {json_col} JSONB
            )
        """)
        # Add GIN index for better JSON query performance
        cursor.execute(f"CREATE INDEX idx_{table_name}_{json_col}_gin ON {table_name} USING GIN ({json_col})")
        # No need to commit with autocommit=True
        logger.info(f"Created FHIR table: {table_name} with JSONB optimization")
    
    def bulk_load_json(self, file_path: str, table_name: str, json_col: str) -> int:
        """Bulk load JSON - PostgreSQL doesn't have direct file reading like DuckDB"""
        # For PostgreSQL, we fall back to individual inserts
        # Could be enhanced with COPY FROM for better performance
        return 0  # Indicates to use fallback method
    
    def insert_resource(self, resource: Dict[str, Any], table_name: str, json_col: str) -> None:
        """Insert a single FHIR resource using JSONB"""
        cursor = self.connection.cursor()
        cursor.execute(
            f"INSERT INTO {table_name} ({json_col}) VALUES (%s)",
            (json.dumps(resource),)
        )
        # No need to commit with autocommit=True
    
    def get_resource_counts(self, table_name: str, json_col: str) -> Dict[str, int]:
        """Get resource counts using JSONB operators"""
        cursor = self.connection.cursor()
        cursor.execute(f"""
            SELECT {json_col}->>'resourceType' as resource_type, COUNT(*) as count 
            FROM {table_name} 
            GROUP BY {json_col}->>'resourceType'
            ORDER BY count DESC
        """)
        return {row[0]: row[1] for row in cursor.fetchall()}
    
    # Dialect-specific SQL generation methods for PostgreSQL
    
    def extract_json_field(self, column: str, path: str) -> str:
        """Extract a JSON field as text using PostgreSQL JSONB operators"""
        if path.startswith('$.'):
            field_path = path[2:]  # Remove $.
            
            # Handle array indexing like name[0].family
            if '[' in field_path:
                import re
                # Convert array indexing: name[0] -> name,0
                processed_path = re.sub(r'(\w+)\[(\d+)\]', r'\1,\2', field_path)
                parts = processed_path.replace('.', ',').split(',')
                # Build the array path correctly for PostgreSQL
                path_elements = []
                for part in parts:
                    if part.isdigit():
                        path_elements.append(part)
                    else:
                        path_elements.append(f'"{part}"')
                path_array = ','.join(path_elements)
                return f"{column} #>> '{{{path_array}}}'"
            elif '.' in field_path:
                # Nested path: $.name.family -> column #>> '{"name","family"}'
                parts = field_path.split('.')
                path_array = ','.join([f'"{part}"' for part in parts])
                return f"{column} #>> '{{{path_array}}}'"
            else:
                # Simple field: $.id -> column ->> 'id'
                return f"{column} ->> '{field_path}'"
        else:
            # Complex JSONPath - use jsonb_path_query_first
            return f"jsonb_path_query_first({column}, '{path}') #>> '{{}}'"
    
    def extract_json_object(self, column: str, path: str) -> str:
        """Extract a JSON object using PostgreSQL JSONB operators"""
        if path.startswith('$.'):
            field_path = path[2:]
            
            # Handle complex paths
            if '[' in field_path or '.' in field_path:
                # Use jsonb_path_query for complex paths
                return f"jsonb_path_query({column}, '{path}')"
            else:
                # Simple field: $.telecom -> column -> 'telecom'
                return f"{column} -> '{field_path}'"
        else:
            # Complex JSONPath
            return f"jsonb_path_query({column}, '{path}')"
    
    def iterate_json_array(self, column: str, path: str) -> str:
        """Iterate over JSON array elements using PostgreSQL JSONB functions"""
        if path.startswith('$.'):
            field_path = path[2:]
            
            if '.' in field_path:
                # Nested path like $.name -> jsonb_array_elements(column -> 'name') WITH ORDINALITY
                parts = field_path.split('.')
                path_expr = column
                for part in parts:
                    path_expr = f"{path_expr} -> '{part}'"
                return f"jsonb_array_elements({path_expr}) WITH ORDINALITY"
            else:
                # Simple path like $.telecom -> jsonb_array_elements(column -> 'telecom') WITH ORDINALITY
                return f"jsonb_array_elements({column} -> '{field_path}') WITH ORDINALITY"
        else:
            # Complex path or no path - if path is '$', it's an array iteration
            if path == '$':
                return f"jsonb_array_elements({column}) WITH ORDINALITY"
            else:
                return f"jsonb_each({column})"
    
    def check_json_exists(self, column: str, path: str) -> str:
        """Check if JSON path exists using PostgreSQL JSONB operators"""
        if path.startswith('$.'):
            field_path = path[2:]
            if '.' not in field_path and '[' not in field_path:
                # Simple path: use ? operator
                return f"({column} ? '{field_path}')"
            else:
                # Complex path: use jsonb_path_exists
                return f"jsonb_path_exists({column}, '{path}')"
        else:
            return f"jsonb_path_exists({column}, '{path}')"
    
    def get_json_type(self, column: str) -> str:
        """Get JSON value type using PostgreSQL's jsonb_typeof with uppercase for case consistency"""
        return f"upper(jsonb_typeof({column}))"
    
    def get_json_array_length(self, column: str, path: str = None) -> str:
        """Get JSON array length using PostgreSQL's jsonb_array_length"""
        if path:
            json_obj = self.extract_json_object(column, path)
            return f"jsonb_array_length({json_obj})"
        else:
            return f"jsonb_array_length({column})"
    
    def get_json_type_constant(self, json_type: str) -> str:
        """Get the correct type constant for comparison with get_json_type()"""
        # Since we use upper(jsonb_typeof()), type constants should be uppercase
        return json_type.upper()
    
    def aggregate_to_json_array(self, expression: str) -> str:
        """Aggregate values into a JSON array using PostgreSQL's jsonb_agg"""
        return f"jsonb_agg({expression})"
    
    def coalesce_empty_array(self, expression: str) -> str:
        """COALESCE with empty array using PostgreSQL JSONB syntax"""
        return f"COALESCE({expression}, '[]'::jsonb)"
    
    def get_array_iteration_columns(self) -> tuple:
        """Get column names for array iteration - PostgreSQL uses 'value' and 'ordinality'"""
        return ('value', 'ordinality')
    
    def get_object_iteration_columns(self) -> tuple:
        """Get column names for object iteration - PostgreSQL uses 'key' and 'value'"""
        return ('key', 'value')
    
    def _apply_database_specific_sql_transforms(self, sql: str) -> str:
        """Apply PostgreSQL-specific SQL transformations"""
        # All SQL generation now uses dialect-aware methods directly
        # No transformations needed
        return sql
    
    def join_array_elements(self, base_expr: str, separator_sql: str) -> str:
        """Join array elements with separator using PostgreSQL's jsonb functions"""
        return f"""
        CASE 
            WHEN {base_expr} IS NULL THEN ''
            ELSE COALESCE((
                SELECT string_agg(
                    CASE 
                        WHEN jsonb_typeof(inner_elem.value) = 'string' THEN inner_elem.value #>> '{{}}'
                        ELSE inner_elem.value::text
                    END, 
                    {separator_sql}
                    ORDER BY outer_elem.outer_ord, inner_elem.inner_ord
                )
                FROM (
                    SELECT 
                        CASE 
                            WHEN jsonb_typeof({base_expr}) = 'array' THEN {base_expr}
                            ELSE jsonb_build_array({base_expr})
                        END as array_val
                ) base_array,
                jsonb_array_elements(base_array.array_val) WITH ORDINALITY AS outer_elem(value, outer_ord),
                jsonb_array_elements(
                    CASE 
                        WHEN jsonb_typeof(outer_elem.value) = 'array' THEN outer_elem.value
                        ELSE jsonb_build_array(outer_elem.value)
                    END
                ) WITH ORDINALITY AS inner_elem(value, inner_ord)
                WHERE inner_elem.value IS NOT NULL AND inner_elem.value != 'null'::jsonb
            ), '')
        END
        """
    
    def extract_nested_array_path(self, json_base: str, current_path: str, identifier_name: str, new_path: str) -> str:
        """Extract path from nested array structures using PostgreSQL's JSONB functions"""
        # Handle root level access (current_path = "$")
        if current_path == "$":
            return f"""CASE WHEN jsonb_typeof({json_base}) = 'array'
            THEN jsonb_path_query_array({json_base}, '$[*].{identifier_name}')
            ELSE {json_base} -> '{identifier_name}'
            END"""
        
        # Convert DuckDB JSONPath syntax to PostgreSQL syntax
        if current_path.startswith('$.'):
            # Convert $.name to 'name' for PostgreSQL JSONB operators
            current_field = current_path[2:]  # Remove $.
            new_field_path = new_path[2:]     # Remove $.
            
            # Handle nested paths like $.name.given
            if '.' in current_field:
                # For nested paths, use jsonb_path_query for more complex operations
                array_path = f"{current_path}[*].{identifier_name}"
                return f"""CASE WHEN jsonb_typeof(({json_base} #> '{{{current_field.replace('.', ',')}}}')) = 'array'
                THEN jsonb_path_query_array({json_base}, '{array_path}')
                ELSE ({json_base} #> '{{{new_field_path.replace('.', ',')}}}')
                END"""
            else:
                # Simple paths like $.name
                array_path = f"{current_path}[*].{identifier_name}"
                return f"""CASE WHEN jsonb_typeof({json_base} -> '{current_field}') = 'array'
                THEN jsonb_path_query_array({json_base}, '{array_path}')
                ELSE {json_base} -> '{current_field}' -> '{identifier_name}'
                END"""
        else:
            # Handle complex paths with jsonb_path_query
            array_path = f"{current_path}[*].{identifier_name}"
            return f"""CASE WHEN jsonb_path_exists({json_base}, '{current_path}') AND jsonb_typeof(jsonb_path_query_first({json_base}, '{current_path}')) = 'array'
            THEN jsonb_path_query_array({json_base}, '{array_path}')
            ELSE jsonb_path_query_first({json_base}, '{new_path}')
            END"""
    
    def split_string(self, expression: str, delimiter: str) -> str:
        """Split string into array using PostgreSQL's string_to_array function"""
        return f"string_to_array(CAST({expression} AS TEXT), {delimiter})"
    
    def substring(self, expression: str, start: str, length: str) -> str:
        """Extract substring using PostgreSQL's SUBSTRING function"""
        return f"SUBSTRING({expression}, ({start}) + 1, {length})"
    
    def string_position(self, search_str: str, target_str: str) -> str:
        """Find position using PostgreSQL's POSITION function (0-based index)"""
        return f"CASE WHEN POSITION(CAST({search_str} AS TEXT) IN CAST({target_str} AS TEXT)) > 0 THEN POSITION(CAST({search_str} AS TEXT) IN CAST({target_str} AS TEXT)) - 1 ELSE -1 END"
    
    def string_concat(self, left: str, right: str) -> str:
        """Concatenate strings using PostgreSQL's || operator"""
        return f"({left} || {right})"
    
    def optimize_cte_definition(self, cte_name: str, cte_expr: str) -> str:
        """Apply PostgreSQL-specific CTE optimizations using MATERIALIZED/NOT MATERIALIZED hints"""
        should_materialize = self._should_materialize_cte(cte_expr)
        
        if should_materialize:
            return f"{cte_name} AS MATERIALIZED ({cte_expr})"
        else:
            return f"{cte_name} AS NOT MATERIALIZED ({cte_expr})"
    
    def _should_materialize_cte(self, cte_expr: str) -> bool:
        """
        Determine if a CTE should be materialized in PostgreSQL
        
        MATERIALIZED CTEs are beneficial when:
        - The CTE produces large intermediate results
        - The CTE is referenced multiple times
        - The CTE contains expensive operations (joins, aggregations)
        """
        # Check for expensive operations that benefit from materialization
        expensive_operations = [
            'jsonb_agg',         # Aggregation operations
            'jsonb_array_elements',  # Table-valued functions
            'GROUP BY',          # Explicit grouping
            'ORDER BY',          # Sorting operations
            'DISTINCT',          # Deduplication
            'CASE WHEN'          # Complex conditional logic
        ]
        
        # Check for multiple expensive operations or very long expressions
        expensive_count = sum(1 for op in expensive_operations if op in cte_expr.upper())
        
        return (
            len(cte_expr) > 500 or           # Large/complex CTEs
            expensive_count >= 2 or          # Multiple expensive operations
            'jsonb_agg' in cte_expr          # Always materialize aggregations
        )

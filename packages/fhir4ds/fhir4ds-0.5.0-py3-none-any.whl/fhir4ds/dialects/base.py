"""
Base database dialect interface for FHIR4DS.

This module defines the abstract base class that all database dialects
must implement to support FHIR data storage and querying.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..datastore import QueryResult
import re


class DatabaseDialect(ABC):
    """Abstract base class for database dialect implementations"""
    
    # FHIR type to SQL type mapping (common across dialects)
    FHIR_TYPE_MAP = {
        "base64Binary": "text",
        "boolean": "boolean", 
        "canonical": "text",
        "code": "text",
        "date": "date",
        "dateTime": "timestamp",
        "decimal": "decimal",
        "id": "text",
        "instant": "timestamp",
        "integer": "integer",
        "integer64": "bigint",
        "markdown": "text",
        "oid": "text",
        "string": "text",
        "positiveInt": "integer",
        "time": "time",
        "unsignedInt": "integer",
        "uri": "text",
        "url": "text",
        "uuid": "text",
        "xhtml": "text"
    }
    
    def __init__(self):
        """Initialize dialect with default properties"""
        self.name = self.__class__.__name__.replace('Dialect', '').upper()
        self.supports_jsonb = False
        self.supports_json_functions = True
        self.json_type = "JSON"
        self.json_extract_function = "json_extract"
        self.json_extract_string_function = "json_extract_string"
        self.json_array_function = "json_array"
        self.json_object_function = "json_object"
        self.json_type_function = "json_type"
        self.json_array_length_function = "json_array_length"
        self.json_each_function = "json_each"
        self.array_agg_function = "array_agg"
        self.string_agg_function = "string_agg"
        self.regex_function = "regexp_extract"
        self.cast_syntax = "::"
        self.quote_char = '"'
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _handle_operation_error(self, operation: str, error: Exception, sql: str = None) -> None:
        """Standard error handling for dialect operations"""
        error_msg = f"{self.name} {operation} failed: {error}"
        if sql:
            error_msg += f"\nSQL: {sql[:200]}..." if len(sql) > 200 else f"\nSQL: {sql}"
        self.logger.error(error_msg)
        raise RuntimeError(error_msg) from error
    
    def _handle_fallback_warning(self, operation: str, error: Exception, fallback_description: str) -> None:
        """Standard warning logging for fallback operations"""
        self.logger.warning(f"{self.name} {operation} failed, using {fallback_description}: {error}")
    
    @abstractmethod
    def get_connection(self) -> Any:
        """Get the underlying database connection"""
        pass
    
    @abstractmethod
    def execute_sql(self, sql: str, view_def: Optional[Dict] = None) -> 'QueryResult':
        """Execute SQL and return results"""
        pass
    
    @abstractmethod
    def create_fhir_table(self, table_name: str, json_col: str) -> None:
        """Create the FHIR resources table"""
        pass
    
    @abstractmethod
    def bulk_load_json(self, file_path: str, table_name: str, json_col: str) -> int:
        """Attempt bulk loading from JSON file, return number of resources loaded"""
        pass
    
    @abstractmethod
    def insert_resource(self, resource: Dict[str, Any], table_name: str, json_col: str) -> None:
        """Insert a single FHIR resource"""
        pass
    
    @abstractmethod
    def get_resource_counts(self, table_name: str, json_col: str) -> Dict[str, int]:
        """Get counts by resource type"""
        pass
    
    @abstractmethod
    def execute_query(self, sql: str) -> Any:
        """Execute a query and return raw results for FHIRResultSet"""
        pass
    
    @abstractmethod
    def get_query_description(self, connection: Any) -> Any:
        """Get column descriptions from last executed query"""
        pass
    
    # SQL Function Translation Methods
    
    def json_extract(self, column: str, path: str) -> str:
        """Generate JSON extraction SQL for the dialect"""
        return f"{self.json_extract_function}({column}, '{path}')"
    
    def json_extract_string(self, column: str, path: str) -> str:
        """Generate JSON string extraction SQL for the dialect"""
        return f"{self.json_extract_string_function}({column}, '{path}')"
    
    def json_type_check(self, column: str, path: str = None) -> str:
        """Generate JSON type checking SQL for the dialect"""
        if path:
            return f"{self.json_type_function}({self.json_extract_function}({column}, '{path}'))"
        return f"{self.json_type_function}({column})"
    
    def json_array_length(self, column: str, path: str = None) -> str:
        """Generate JSON array length SQL for the dialect"""
        if path:
            return f"{self.json_array_length_function}({self.json_extract_function}({column}, '{path}'))"
        return f"{self.json_array_length_function}({column})"
    
    def json_each(self, column: str, path: str = None) -> str:
        """Generate JSON each iteration SQL for the dialect"""
        if path:
            return f"{self.json_each_function}({self.json_extract_function}({column}, '{path}'))"
        return f"{self.json_each_function}({column})"
    
    def array_agg(self, expression: str, distinct: bool = False) -> str:
        """Generate array aggregation SQL for the dialect"""
        if distinct:
            return f"{self.array_agg_function}(DISTINCT {expression})"
        return f"{self.array_agg_function}({expression})"
    
    def string_agg(self, expression: str, separator: str, distinct: bool = False) -> str:
        """Generate string aggregation SQL for the dialect"""
        if distinct:
            return f"{self.string_agg_function}(DISTINCT {expression}, {separator})"
        return f"{self.string_agg_function}({expression}, {separator})"
    
    def regex_extract(self, column: str, pattern: str, group: int = 1) -> str:
        """Generate regex extraction SQL for the dialect"""
        return f"{self.regex_function}({column}, '{pattern}', {group})"
    
    def cast_to_type(self, expression: str, target_type: str) -> str:
        """Generate type casting SQL for the dialect"""
        return f"{expression}{self.cast_syntax}{target_type}"
    
    def quote_identifier(self, identifier: str) -> str:
        """Quote an identifier for the dialect"""
        return f"{self.quote_char}{identifier}{self.quote_char}"
    
    def translate_sql(self, sql: str) -> str:
        """
        Translate SQL from DuckDB format to this dialect.
        This is the main function that converts SQL queries.
        """
        translated = sql
        
        # Replace function calls
        function_mappings = {
            'json_extract': self.json_extract_function,
            'json_extract_string': self.json_extract_string_function, 
            'json_type': self.json_type_function,
            'json_array_length': self.json_array_length_function,
            'json_each': self.json_each_function,
            'json_array': self.json_array_function,
            'json_object': self.json_object_function,
            'array_agg': self.array_agg_function,
            'string_agg': self.string_agg_function
        }
        
        for duckdb_func, dialect_func in function_mappings.items():
            if duckdb_func != dialect_func:
                # Use word boundaries to avoid partial replacements
                pattern = r'\b' + re.escape(duckdb_func) + r'\b'
                translated = re.sub(pattern, dialect_func, translated)
        
        return self._apply_dialect_specific_transforms(translated)
    
    def _apply_dialect_specific_transforms(self, sql: str) -> str:
        """Apply dialect-specific transformations. Override in subclasses."""
        return sql
    
    def supports_feature(self, feature: str) -> bool:
        """Check if dialect supports a specific feature"""
        features = {
            'jsonb': self.supports_jsonb,
            'json_functions': self.supports_json_functions,
            'regex': hasattr(self, 'regex_function'),
            'array_functions': True  # Most dialects support basic array functions
        }
        return features.get(feature, False)
    
    # Abstract dialect-specific SQL generation methods
    # These should be implemented by each dialect
    
    @abstractmethod
    def extract_json_field(self, column: str, path: str) -> str:
        """Extract a JSON field as text - database specific implementation"""
        pass
    
    @abstractmethod 
    def extract_json_object(self, column: str, path: str) -> str:
        """Extract a JSON object - database specific implementation"""
        pass
    
    @abstractmethod
    def iterate_json_array(self, column: str, path: str) -> str:
        """Iterate over JSON array elements - database specific implementation"""
        pass
    
    @abstractmethod
    def check_json_exists(self, column: str, path: str) -> str:
        """Check if JSON path exists - database specific implementation"""
        pass
    
    @abstractmethod
    def get_json_type(self, column: str) -> str:
        """Get JSON value type - database specific implementation"""
        pass
    
    def json_type(self, column: str) -> str:
        """Alias for get_json_type for backward compatibility"""
        return self.get_json_type(column)
    
    @abstractmethod
    def get_json_array_length(self, column: str, path: str = None) -> str:
        """Get JSON array length - database specific implementation"""
        pass
    
    def get_json_type_constant(self, json_type: str) -> str:
        """Get the correct type constant for comparison with get_json_type()"""
        # Default implementation - return uppercase for consistency
        return json_type.upper()
    
    @abstractmethod
    def aggregate_to_json_array(self, expression: str) -> str:
        """Aggregate values into a JSON array - database specific implementation"""
        pass
    
    @abstractmethod
    def coalesce_empty_array(self, expression: str) -> str:
        """COALESCE with empty array - database specific implementation"""
        pass

    @abstractmethod 
    def join_array_elements(self, base_expr: str, separator_sql: str) -> str:
        """Join array elements with separator - database specific implementation"""
        pass
    
    @abstractmethod
    def extract_nested_array_path(self, json_base: str, current_path: str, identifier_name: str, new_path: str) -> str:
        """Extract path from nested array structures with proper flattening - database specific implementation"""
        pass
    
    @abstractmethod
    def split_string(self, expression: str, delimiter: str) -> str:
        """Split string into array using delimiter - database specific implementation"""
        pass
    
    @abstractmethod
    def substring(self, expression: str, start: str, length: str) -> str:
        """Extract substring from string - database specific implementation"""
        pass
    
    @abstractmethod
    def string_position(self, search_str: str, target_str: str) -> str:
        """Find position of search string in target string - database specific implementation"""
        pass
    
    @abstractmethod
    def string_concat(self, left: str, right: str) -> str:
        """Concatenate two strings - database specific implementation"""
        pass
    
    def optimize_cte_definition(self, cte_name: str, cte_expr: str) -> str:
        """Apply dialect-specific CTE optimizations - database specific implementation"""
        # Default implementation - no optimization
        return f"{cte_name} AS ({cte_expr})"
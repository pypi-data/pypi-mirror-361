"""
FHIR Query Result Handling

QueryResult class (renamed from FHIRResultSet) providing:
- Query execution and result caching
- DataFrame and CSV export functionality  
- Collection column processing
- Fluent interface for result conversion
"""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Any, Optional

# Optional imports for functionality
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import csv
    import io
    CSV_AVAILABLE = True
except ImportError:
    CSV_AVAILABLE = False

logger = logging.getLogger(__name__)


class QueryResult:
    """
    Unified result set that provides DataFrame and CSV export functionality
    regardless of the underlying database dialect.
    """
    
    def __init__(self, dialect, sql: str, view_def: Optional[Dict] = None):
        self.dialect = dialect
        self.sql = sql
        self.view_def = view_def
        self._executed = False
        self._result = None
        self._description = None
    
    def fetchall(self) -> List[tuple]:
        """Fetch all rows from the query result"""
        if not self._executed:
            # Use the new abstract methods to avoid dialect-specific code
            raw_result = self.dialect.execute_query(self.sql)
            self._description = self.dialect.get_query_description(self.dialect.get_connection())
            
            # Process collection columns if view_def is available
            if self.view_def:
                self._result = self._convert_collection_columns_to_arrays(raw_result)
            else:
                self._result = raw_result
                
            self._executed = True
        return self._result
    
    # Fluent interface methods for result conversion
    def to_dataframe(self, include_metadata: bool = True) -> 'pd.DataFrame':
        """Convert results to pandas DataFrame for fluent chaining"""
        return self.to_df(include_metadata)
    
    @property
    def description(self):
        """Get column descriptions"""
        if not self._executed:
            self.fetchall()
        return self._description
    
    @property
    def sql(self) -> str:
        """Get the SQL query that was executed"""
        return self._sql
    
    @sql.setter
    def sql(self, value: str):
        """Set the SQL query"""
        self._sql = value
        # Reset execution state when SQL changes
        self._executed = False
        self._result = None
        self._description = None
    
    def to_df(self, include_metadata: bool = True) -> 'pd.DataFrame':
        """Convert results to pandas DataFrame with proper column names"""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for to_df(). Install with: pip install pandas")
        
        rows = self.fetchall()
        column_names = self._get_column_names_from_view_definition()
        
        # Create DataFrame
        if rows:
            df = pd.DataFrame(rows, columns=column_names)
        else:
            df = pd.DataFrame(columns=column_names)
        
        # Add metadata
        if include_metadata and self.view_def:
            df.attrs['view_name'] = self.view_def.get('name', 'unnamed_view')
            df.attrs['resource_type'] = self.view_def.get('resource', 'unknown')
            df.attrs['description'] = self.view_def.get('description', '')
            df.attrs['total_rows'] = len(rows)
            df.attrs['sql_query'] = self.sql
            df.attrs['dialect'] = type(self.dialect).__name__
        
        return df
    
    def to_csv(self, file_path: Optional[str] = None, include_headers: bool = True, **kwargs) -> Optional[str]:
        """Convert results to CSV format"""
        if not CSV_AVAILABLE:
            raise ImportError("csv module is required for to_csv()")
        
        rows = self.fetchall()
        column_names = self._get_column_names_from_view_definition()
        
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, **kwargs)
                if include_headers:
                    writer.writerow(column_names)
                writer.writerows(rows)
            return None
        else:
            output = io.StringIO()
            writer = csv.writer(output, **kwargs)
            if include_headers:
                writer.writerow(column_names)
            writer.writerows(rows)
            return output.getvalue()
    
    def _get_column_names_from_view_definition(self) -> List[str]:
        """Get column names from view definition or connection description"""
        if self.view_def:
            return self._parse_column_names_from_view_definition()
        else:
            if not self._executed:
                self.fetchall()
            return [desc[0] for desc in (self._description or [])]
    
    def _parse_column_names_from_view_definition(self) -> List[str]:
        """Parse column names from view definition structure"""
        column_names = []
        
        def extract_from_select_items(select_items: List[Dict[str, Any]]):
            for select_item in select_items:
                if 'path' in select_item and 'name' in select_item:
                    column_names.append(select_item['name'])
                elif 'column' in select_item:
                    for column in select_item['column']:
                        if 'name' in column:
                            column_names.append(column['name'])
                if 'select' in select_item:
                    extract_from_select_items(select_item['select'])
                if 'unionAll' in select_item and select_item['unionAll']:
                    first_branch = select_item['unionAll'][0]
                    if 'column' in first_branch:
                        for column in first_branch['column']:
                            if 'name' in column and column['name'] not in column_names:
                                column_names.append(column['name'])
                    elif 'select' in first_branch:
                        extract_from_select_items(first_branch['select'])
        
        if 'select' in self.view_def:
            extract_from_select_items(self.view_def['select'])
        
        if not column_names:
            if not self._executed:
                self.fetchall()
            column_names = [desc[0] for desc in (self._description or [])]
        
        return column_names
    
    def _convert_collection_columns_to_arrays(self, raw_result):
        """Convert JSON strings to arrays for collection columns"""
        if not raw_result or not self.view_def:
            return raw_result
        
        column_names = [desc[0] for desc in self._description or []]
        collection_columns = self._get_collection_columns()
        
        processed_result = []
        for row in raw_result:
            processed_row = list(row)
            
            for col_name in collection_columns:
                if col_name in column_names:
                    col_index = column_names.index(col_name)
                    if col_index < len(processed_row):
                        value = processed_row[col_index]
                        
                        # Handle both DuckDB (JSON strings) and PostgreSQL (native types)
                        if isinstance(value, str) and value.startswith('['):
                            # DuckDB case: parse JSON string
                            try:
                                parsed_value = json.loads(value)
                                processed_row[col_index] = parsed_value
                            except:
                                pass
                        elif isinstance(value, list):
                            # PostgreSQL case: already a list, use as-is
                            processed_row[col_index] = value
            
            processed_result.append(tuple(processed_row))
        
        return processed_result
    
    def _get_collection_columns(self):
        """Get list of column names that have collection: true"""
        collection_columns = []
        
        def extract_collection_columns(select_items):
            for select_item in select_items:
                if 'column' in select_item:
                    for column in select_item['column']:
                        if column.get('collection') is True:
                            collection_columns.append(column['name'])
                if 'select' in select_item:
                    extract_collection_columns(select_item['select'])
                if 'unionAll' in select_item:
                    for union_item in select_item['unionAll']:
                        if 'column' in union_item:
                            for column in union_item['column']:
                                if column.get('collection') is True:
                                    collection_columns.append(column['name'])
        
        if 'select' in self.view_def:
            extract_collection_columns(self.view_def['select'])
        
        return collection_columns
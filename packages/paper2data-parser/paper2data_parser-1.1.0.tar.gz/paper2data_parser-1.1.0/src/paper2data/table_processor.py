import csv
import io
import re
from typing import List, Dict, Any, Optional, Tuple
from .utils import get_logger

logger = get_logger(__name__)

class TableProcessor:
    """Enhanced table processor for converting raw table text to structured CSV format."""
    
    def __init__(self):
        self.confidence_threshold = 0.5
        
    def convert_to_csv(self, raw_table_text: str, table_id: str) -> Optional[Dict[str, Any]]:
        """
        Convert raw table text to structured CSV format.
        
        Args:
            raw_table_text: Raw text extracted from table
            table_id: Unique identifier for the table
            
        Returns:
            Dictionary containing CSV data and metadata, or None if conversion fails
        """
        try:
            # Split into lines and clean
            lines = [line.strip() for line in raw_table_text.split('\n') if line.strip()]
            
            if len(lines) < 2:  # Need at least header + 1 data row
                return None
                
            # Detect and process header
            header_info = self._detect_header(lines)
            if not header_info:
                return None
                
            header_line_idx, header_columns = header_info
            
            # Process data rows
            data_rows = self._process_data_rows(lines[header_line_idx + 1:], len(header_columns))
            
            if not data_rows:
                return None
                
            # Create CSV content
            csv_content = self._create_csv_content(header_columns, data_rows)
            
            # Calculate confidence score
            confidence = self._calculate_csv_confidence(header_columns, data_rows)
            
            return {
                'table_id': table_id,
                'csv_content': csv_content,
                'header_columns': header_columns,
                'data_rows': data_rows,
                'row_count': len(data_rows),
                'column_count': len(header_columns),
                'confidence': confidence,
                'format': 'csv'
            }
            
        except Exception as e:
            logger.warning(f"Failed to convert table {table_id} to CSV: {str(e)}")
            return None
    
    def _detect_header(self, lines: List[str]) -> Optional[Tuple[int, List[str]]]:
        """
        Detect table header from lines of text.
        
        Returns:
            Tuple of (header_line_index, header_columns) or None
        """
        for i, line in enumerate(lines[:3]):  # Check first 3 lines for header
            columns = self._split_table_line(line)
            
            if len(columns) >= 2:  # Need at least 2 columns
                # Check if this looks like a header
                if self._is_likely_header(columns):
                    return (i, columns)
                    
        return None
    
    def _is_likely_header(self, columns: List[str]) -> bool:
        """Check if columns look like table headers."""
        if not columns:
            return False
            
        # Header indicators
        header_patterns = [
            r'\b(name|type|value|amount|date|time|method|result|score)\b',
            r'\b(total|average|count|number|percent|rate)\b',
            r'\b(id|identifier|code|reference)\b'
        ]
        
        # Count columns that match header patterns
        header_like_count = 0
        for col in columns:
            col_lower = col.lower()
            for pattern in header_patterns:
                if re.search(pattern, col_lower):
                    header_like_count += 1
                    break
                    
        # Also check for title case or all caps (common in headers)
        title_case_count = sum(1 for col in columns if col.istitle() or col.isupper())
        
        # Consider it a header if many columns are header-like or title case
        return (header_like_count >= len(columns) // 2) or (title_case_count >= len(columns) // 2)
    
    def _split_table_line(self, line: str) -> List[str]:
        """Split a table line into columns using various delimiters."""
        # Try different splitting strategies
        
        # Strategy 1: Tab separated
        if '\t' in line:
            columns = [col.strip() for col in line.split('\t')]
            if len(columns) >= 2:
                return [col for col in columns if col]  # Remove empty columns
        
        # Strategy 2: Multiple spaces (2 or more)
        columns = re.split(r'\s{2,}', line.strip())
        if len(columns) >= 2:
            return [col.strip() for col in columns if col.strip()]
            
        # Strategy 3: Pipe separated
        if '|' in line:
            columns = [col.strip() for col in line.split('|')]
            return [col for col in columns if col]
            
        # Strategy 4: Single space (fallback)
        columns = line.split()
        if len(columns) >= 2:
            return columns
            
        return []
    
    def _process_data_rows(self, lines: List[str], expected_columns: int) -> List[List[str]]:
        """Process data rows ensuring consistent column count."""
        data_rows = []
        
        for line in lines:
            columns = self._split_table_line(line)
            
            if not columns:
                continue
                
            # Adjust column count to match header
            if len(columns) < expected_columns:
                # Pad with empty strings
                columns.extend([''] * (expected_columns - len(columns)))
            elif len(columns) > expected_columns:
                # Truncate or merge excess columns
                if expected_columns > 0:
                    # Merge excess columns into the last column
                    merged_last = ' '.join(columns[expected_columns-1:])
                    columns = columns[:expected_columns-1] + [merged_last]
                    
            data_rows.append(columns[:expected_columns])
            
        return data_rows
    
    def _create_csv_content(self, header: List[str], data_rows: List[List[str]]) -> str:
        """Create CSV content from header and data rows."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        writer.writerow(header)
        
        # Write data rows
        for row in data_rows:
            writer.writerow(row)
            
        return output.getvalue()
    
    def _calculate_csv_confidence(self, header: List[str], data_rows: List[List[str]]) -> float:
        """Calculate confidence score for CSV conversion quality."""
        confidence = 0.6  # Base confidence
        
        # Bonus for good header
        if len(header) >= 3:
            confidence += 0.2
            
        # Bonus for consistent data
        if len(data_rows) >= 3:
            confidence += 0.1
            
        # Check for numeric data (good indicator)
        numeric_columns = 0
        for col_idx in range(len(header)):
            numeric_count = 0
            for row in data_rows:
                if col_idx < len(row):
                    if re.match(r'^[\d,.-]+$', row[col_idx].strip()):
                        numeric_count += 1
            if numeric_count > len(data_rows) * 0.5:  # More than half numeric
                numeric_columns += 1
                
        if numeric_columns > 0:
            confidence += 0.1 * min(numeric_columns, 3) / 3  # Up to 0.1 bonus
            
        return min(confidence, 1.0)

def enhance_table_with_csv(table_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance existing table data with CSV conversion.
    
    Args:
        table_data: Original table data with raw_text
        
    Returns:
        Enhanced table data with CSV format
    """
    processor = TableProcessor()
    
    if 'raw_text' not in table_data:
        return table_data
        
    csv_result = processor.convert_to_csv(
        table_data['raw_text'], 
        table_data.get('table_id', 'unknown')
    )
    
    if csv_result:
        # Merge CSV data into original table data
        table_data.update(csv_result)
        logger.info(f"Successfully converted table {table_data.get('table_id', 'unknown')} to CSV format")
    else:
        logger.warning(f"Failed to convert table {table_data.get('table_id', 'unknown')} to CSV format")
        
    return table_data 
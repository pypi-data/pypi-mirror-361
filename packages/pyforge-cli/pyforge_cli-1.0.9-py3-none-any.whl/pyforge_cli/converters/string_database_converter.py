"""
Base database converter with string-only output for Phase 1.
All data types converted to string format per PRD specifications.
"""

import logging
import shutil
import tempfile
from abc import abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ..detectors.database_detector import DatabaseInfo
from .base import BaseConverter


@dataclass
class ConversionStats:
    """Statistics for string conversion process"""

    total_records: int = 0
    total_fields: int = 0
    conversions_by_type: Dict[str, int] = None
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.conversions_by_type is None:
            self.conversions_by_type = {}
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class StringTypeConverter:
    """
    Converts various data types to string format per Phase 1 specifications.

    Conversion Rules:
    - Numbers: Decimal format with 5 precision, no trailing zeros
    - Dates: ISO 8601 format
    - Booleans: "true"/"false" lowercase
    - Binary: Base64 encoding
    - NULL: Empty string
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.stats = ConversionStats()

    def convert_value(self, value: Any, source_type: Optional[str] = None) -> str:
        """
        Convert any value to string format according to Phase 1 rules.

        Args:
            value: The value to convert
            source_type: Optional hint about source data type

        Returns:
            String representation of the value
        """
        try:
            # Track conversion by detected type
            detected_type = self._detect_type(value, source_type)
            self.stats.conversions_by_type[detected_type] = (
                self.stats.conversions_by_type.get(detected_type, 0) + 1
            )

            # Handle None/NULL values
            if value is None or pd.isna(value):
                return ""

            # Handle different data types
            if isinstance(value, bool):
                return self._convert_boolean(value)
            elif isinstance(value, (int, float, Decimal)):
                return self._convert_number(value)
            elif isinstance(value, (datetime, date, time)):
                return self._convert_datetime(value)
            elif isinstance(value, bytes):
                return self._convert_binary(value)
            elif isinstance(value, str):
                return self._convert_string(value)
            else:
                # Fallback: convert to string
                return str(value)

        except Exception as e:
            # Handle cases where repr() or str() also fail
            try:
                value_repr = repr(value)
            except Exception:
                value_repr = f"<object of type {type(value).__name__}>"

            try:
                error_msg = f"Error converting value {value_repr}: {str(e)}"
            except Exception:
                error_msg = (
                    f"Error converting value {value_repr}: <error details unavailable>"
                )

            self.logger.warning(error_msg)
            self.stats.errors.append(error_msg)

            # Return original value as string on error
            try:
                return str(value) if value is not None else ""
            except Exception:
                return "[CONVERSION_ERROR]"

    def _detect_type(self, value: Any, hint: Optional[str] = None) -> str:
        """Detect the type of value for statistics"""
        if value is None or pd.isna(value):
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, Decimal):
            return "decimal"
        elif isinstance(value, datetime):
            return "datetime"
        elif isinstance(value, date):
            return "date"
        elif isinstance(value, time):
            return "time"
        elif isinstance(value, bytes):
            return "binary"
        elif isinstance(value, str):
            return "string"
        else:
            return "other"

    def _convert_boolean(self, value: bool) -> str:
        """Convert boolean to lowercase string"""
        return "true" if value else "false"

    def _convert_number(self, value: Union[int, float, Decimal]) -> str:
        """
        Convert number to string with 5 decimal precision.
        Remove trailing zeros but keep at least one decimal place for floats.
        """
        try:
            # Handle integer values
            if isinstance(value, int):
                return str(value)

            # Convert to Decimal for precision control
            if isinstance(value, float):
                # Handle special float values
                if pd.isna(value) or value != value:  # NaN check
                    return ""
                if value == float("inf"):
                    return "Infinity"
                if value == float("-inf"):
                    return "-Infinity"

                decimal_val = Decimal(str(value))
            else:
                decimal_val = value

            # Format with 5 decimal places
            formatted = f"{decimal_val:.5f}"

            # Remove trailing zeros, but keep at least one decimal if it was a float
            if "." in formatted:
                formatted = formatted.rstrip("0")
                if formatted.endswith("."):
                    if isinstance(value, (float, Decimal)) and not isinstance(
                        value, int
                    ):
                        formatted += "0"  # Keep .0 for floats
                    else:
                        formatted = formatted[:-1]  # Remove . for integers

            return formatted

        except (InvalidOperation, ValueError) as e:
            self.stats.warnings.append(f"Number conversion error for {value}: {e}")
            return str(value)

    def _convert_datetime(self, value: Union[datetime, date, time]) -> str:
        """Convert datetime objects to ISO 8601 format"""
        try:
            if isinstance(value, datetime):
                # Full datetime: YYYY-MM-DD HH:MM:SS
                return value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, date):
                # Date only: YYYY-MM-DD
                return value.strftime("%Y-%m-%d")
            elif isinstance(value, time):
                # Time only: HH:MM:SS
                return value.strftime("%H:%M:%S")
            else:
                return str(value)

        except Exception as e:
            self.stats.warnings.append(f"Date conversion error for {value}: {e}")
            return str(value)

    def _convert_binary(self, value: bytes) -> str:
        """Convert binary data to Base64 string"""
        try:
            import base64

            return base64.b64encode(value).decode("ascii")
        except Exception as e:
            self.stats.warnings.append(f"Binary conversion error: {e}")
            return "[BINARY_DATA]"

    def _convert_string(self, value: str) -> str:
        """Process string values (encoding, cleanup)"""
        try:
            # Ensure UTF-8 encoding
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="replace")

            # Basic cleanup - preserve original spacing
            return str(value)

        except Exception as e:
            self.stats.warnings.append(f"String conversion error: {e}")
            return str(value)

    def convert_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert entire DataFrame to string columns.

        Args:
            df: Source DataFrame

        Returns:
            DataFrame with all columns as strings
        """
        if df.empty:
            return df

        # Track overall stats
        self.stats.total_records = len(df)
        self.stats.total_fields = len(df.columns)

        # Convert each column
        string_df = pd.DataFrame()

        for column in df.columns:
            self.logger.debug(f"Converting column: {column}")

            # Convert entire column
            column_dtype = str(df[column].dtype)
            string_column = df[column].apply(
                lambda x, dtype=column_dtype: self.convert_value(x, source_type=dtype)
            )

            string_df[column] = string_column

        # Ensure all columns are string type
        string_df = string_df.astype(str)

        return string_df

    def get_conversion_summary(self) -> Dict[str, Any]:
        """Get summary of conversion statistics"""
        return {
            "total_records": self.stats.total_records,
            "total_fields": self.stats.total_fields,
            "conversions_by_type": dict(self.stats.conversions_by_type),
            "errors": len(self.stats.errors),
            "warnings": len(self.stats.warnings),
            "error_details": self.stats.errors[-10:],  # Last 10 errors
            "warning_details": self.stats.warnings[-10:],  # Last 10 warnings
        }


class StringDatabaseConverter(BaseConverter):
    """
    Base converter for database files with string-only output.
    Provides common functionality for MDB and DBF converters.
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.string_converter = StringTypeConverter()
        self.database_info: Optional[DatabaseInfo] = None
        self.conversion_stats: List[ConversionStats] = []

    @abstractmethod
    def _connect_to_database(self, input_path: Path) -> Any:
        """Connect to database and return connection object"""
        pass

    @abstractmethod
    def _list_tables(self, connection: Any) -> List[str]:
        """List all user tables in the database"""
        pass

    @abstractmethod
    def _read_table(self, connection: Any, table_name: str) -> pd.DataFrame:
        """Read table data as DataFrame"""
        pass

    @abstractmethod
    def _get_table_info(self, connection: Any, table_name: str) -> Dict[str, Any]:
        """Get metadata about a table"""
        pass

    def convert(self, input_path: Path, output_path: Path, **options: Any) -> bool:
        """
        Convert database file to string-based Parquet files.

        Args:
            input_path: Path to source database file
            output_path: Directory for output Parquet files
            **options: Conversion options

        Returns:
            True if conversion successful
        """
        try:
            self.logger.info(f"Starting conversion: {input_path} -> {output_path}")

            # Validate input file
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")

            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)

            # Connect to database
            connection = self._connect_to_database(input_path)

            try:
                # List tables
                tables = self._list_tables(connection)
                self.logger.info(f"Found {len(tables)} tables: {tables}")

                if not tables:
                    self.logger.warning("No tables found in database")
                    return True

                # Convert each table
                for table_name in tables:
                    self.logger.info(f"Converting table: {table_name}")

                    try:
                        # Read table data
                        df = self._read_table(connection, table_name)

                        if df.empty:
                            self.logger.warning(f"Table {table_name} is empty")
                            continue

                        # Convert to strings
                        string_df = self.string_converter.convert_dataframe(df)

                        # Save as Parquet
                        output_file = output_path / f"{table_name}.parquet"
                        self._save_parquet(string_df, output_file, **options)

                        # Track statistics
                        self.conversion_stats.append(self.string_converter.stats)

                        self.logger.info(
                            f"✓ Converted {table_name}: {len(df)} records -> {output_file}"
                        )

                    except Exception as e:
                        self.logger.error(f"Error converting table {table_name}: {e}")
                        # Continue with other tables
                        continue

                return True

            finally:
                self._close_connection(connection)

        except Exception as e:
            self.logger.error(f"Conversion failed: {e}")
            return False

    def _is_volume_path(self, path: Path) -> bool:
        """Check if a path is a Databricks Unity Catalog volume path."""
        return str(path).startswith("/Volumes/")

    def _save_parquet(
        self, df: pd.DataFrame, output_file: Path, **options: Any
    ) -> None:
        """Save DataFrame as Parquet with string schema, handling volume paths safely."""
        try:
            # Parquet options
            compression = options.get("compression", "snappy")

            # Ensure all columns are strings
            string_df = df.copy()
            for col in string_df.columns:
                string_df[col] = string_df[col].astype(str)

            if self._is_volume_path(output_file):
                # Write to temporary file first, then copy to volume
                with tempfile.NamedTemporaryFile(
                    suffix=".parquet", delete=False
                ) as tmp_file:
                    tmp_path = Path(tmp_file.name)

                    # Create PyArrow schema with all string columns
                    schema_fields = [(col, pa.string()) for col in string_df.columns]
                    schema = pa.schema(schema_fields)

                    # Convert to PyArrow table and write
                    table = pa.Table.from_pandas(string_df, schema=schema)
                    pq.write_table(
                        table,
                        tmp_path,
                        compression=compression,
                        write_statistics=True,
                        use_dictionary=True,
                    )

                    # Copy to final destination
                    shutil.copy2(str(tmp_path), str(output_file))
                    tmp_path.unlink()  # Clean up temp file

            else:
                # Direct write for non-volume paths using PyArrow
                # Create PyArrow schema with all string columns
                schema_fields = [(col, pa.string()) for col in string_df.columns]
                schema = pa.schema(schema_fields)

                # Convert to PyArrow table and write
                table = pa.Table.from_pandas(string_df, schema=schema)
                pq.write_table(
                    table,
                    output_file,
                    compression=compression,
                    write_statistics=True,
                    use_dictionary=True,
                )

        except Exception as e:
            self.logger.error(f"Error saving Parquet file {output_file}: {e}")
            raise

    def _close_connection(self, connection: Any) -> None:
        """Close database connection (override if needed)"""
        try:
            if hasattr(connection, "close"):
                connection.close()
        except Exception as e:
            self.logger.warning(f"Error closing connection: {e}")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported input formats"""
        return []  # Override in subclasses

    def validate_input(self, input_path: Path) -> Tuple[bool, str]:
        """Validate input file"""
        from ..detectors.database_detector import DatabaseFileDetector

        detector = DatabaseFileDetector()
        return detector.validate_file_access(input_path)

    def get_conversion_report(self) -> Dict[str, Any]:
        """Generate comprehensive conversion report"""
        if not self.conversion_stats:
            return {"status": "no_conversions"}

        # Aggregate statistics
        total_records = sum(stat.total_records for stat in self.conversion_stats)
        total_fields = sum(stat.total_fields for stat in self.conversion_stats)

        # Combine conversion type counts
        all_conversions = {}
        all_errors = []
        all_warnings = []

        for stat in self.conversion_stats:
            for type_name, count in stat.conversions_by_type.items():
                all_conversions[type_name] = all_conversions.get(type_name, 0) + count
            all_errors.extend(stat.errors)
            all_warnings.extend(stat.warnings)

        return {
            "status": "completed",
            "summary": {
                "total_records": total_records,
                "total_fields": total_fields,
                "tables_processed": len(self.conversion_stats),
                "conversion_types": all_conversions,
                "errors": len(all_errors),
                "warnings": len(all_warnings),
            },
            "details": {
                "error_samples": all_errors[-10:],
                "warning_samples": all_warnings[-10:],
                "conversion_breakdown": all_conversions,
            },
        }


# Example conversion rules demonstration
def demonstrate_string_conversion():
    """Demonstrate string conversion rules with examples"""

    converter = StringTypeConverter()

    test_values = [
        # Numbers
        (42, "integer"),
        (123.4, "float"),
        (123.45678, "float with precision"),
        (Decimal("999.12345"), "decimal"),
        (-45.67, "negative float"),
        (1000000, "large integer"),
        # Dates
        (datetime(2024, 3, 15, 14, 30, 0), "datetime"),
        (date(2024, 3, 15), "date"),
        (time(14, 30, 0), "time"),
        # Booleans
        (True, "boolean true"),
        (False, "boolean false"),
        # Special values
        (None, "null"),
        ("", "empty string"),
        ("Hello World", "regular string"),
        (b"binary data", "binary"),
    ]

    print("String Conversion Rules Demonstration:")
    print("=" * 60)

    for value, description in test_values:
        converted = converter.convert_value(value)
        print(f"{description:25} | {repr(value):20} → {repr(converted)}")

    print("\nConversion Statistics:")
    summary = converter.get_conversion_summary()
    for type_name, count in summary["conversions_by_type"].items():
        print(f"  {type_name}: {count}")


if __name__ == "__main__":
    demonstrate_string_conversion()

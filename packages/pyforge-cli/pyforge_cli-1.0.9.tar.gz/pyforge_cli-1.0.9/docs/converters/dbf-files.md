# DBF File Conversion

Convert dBASE files (.dbf) to efficient Parquet format with automatic encoding detection and robust error handling for legacy database files.

## Overview

PyForge CLI provides comprehensive DBF file conversion with:

- **Automatic encoding detection** for international character sets
- **Multiple DBF format support** (dBASE III, IV, 5.0, Visual FoxPro)
- **Robust error handling** for corrupted or incomplete files
- **Character encoding preservation** with UTF-8 output
- **Memory-efficient processing** for large DBF files
- **Data type optimization** for modern analytics

## Supported DBF Formats

| Format | Version | Extension | Notes |
|--------|---------|-----------|-------|
| **dBASE III** | 3.0 | `.dbf` | Classic format, widely supported |
| **dBASE IV** | 4.0 | `.dbf` | Enhanced field types |
| **dBASE 5.0** | 5.0 | `.dbf` | Extended capabilities |
| **Visual FoxPro** | 6.0-9.0 | `.dbf` | Microsoft variant |
| **Clipper** | Various | `.dbf` | CA-Clipper format |

## Basic Usage

### Simple Conversion

```bash
# Convert DBF file to Parquet
pyforge convert data.dbf

# Output: data.parquet
```

### With Custom Output

```bash
# Specify output file
pyforge convert legacy_data.dbf modern_data.parquet

# Convert to directory
pyforge convert historical.dbf processed/
```

## Encoding Handling

PyForge automatically detects and handles various character encodings:

### Automatic Detection

```bash
# Automatic encoding detection (always enabled)
pyforge convert international.dbf

# Shows processing information in verbose mode
pyforge convert file.dbf --verbose
# Info: Processing DBF file with automatic encoding detection
```

### Encoding Support

PyForge automatically handles common DBF encodings:
- **DOS**: cp437, cp850 (legacy DOS systems)
- **Windows**: cp1252 (Windows Latin-1)  
- **International**: iso-8859-1, iso-8859-2 (European)
- **Cyrillic**: cp866, cp1251 (Russian/Eastern European)
- **Modern**: utf-8 (Unicode standard)

## Advanced Options

### Processing Options

=== "Standard Conversion"
    ```bash
    # Basic conversion with auto-detection
    pyforge convert data.dbf
    ```

=== "Custom Compression"
    ```bash
    # Use different compression
    pyforge convert data.dbf --compression gzip
    ```

=== "Force Overwrite"
    ```bash
    # Overwrite existing output
    pyforge convert data.dbf --force
    ```

=== "Verbose Output"
    ```bash
    # Detailed processing information
    pyforge convert data.dbf --verbose
    ```

### Compression and Output

```bash
# Use compression for smaller files
pyforge convert large_file.dbf --compression gzip

# Force overwrite existing output
pyforge convert data.dbf --force

# Custom chunk size for memory management
pyforge convert huge_file.dbf --chunk-size 50000
```

## Data Type Handling

PyForge converts all DBF data to string format for maximum compatibility:

| DBF Type | DBF Code | Parquet Type | Notes |
|----------|----------|--------------|-------|
| **Character** | C | string | Text fields, UTF-8 encoded |
| **Numeric** | N | string | Decimal precision preserved, no trailing zeros |
| **Date** | D | string | ISO 8601 format (YYYY-MM-DD) |
| **Logical** | L | string | "true" or "false" lowercase strings |
| **Memo** | M | string | Large text fields |
| **Float** | F | string | Floating point values as decimal strings |
| **Currency** | Y | string | Monetary values as decimal strings |
| **DateTime** | T | string | ISO 8601 format (YYYY-MM-DDTHH:MM:SS) |
| **Integer** | I | string | Integer values preserved as strings |
| **Double** | B | string | Double precision values as decimal strings |

!!! note "String-Based Conversion"
    PyForge CLI currently uses a string-based conversion approach to ensure consistent behavior across all database formats (Excel, MDB, DBF). While this preserves data integrity and precision, you may need to cast types in your analysis tools (pandas, Spark, etc.) if you require native numeric or datetime types.

## Error Handling

### Common Issues and Solutions

**Encoding Problems**:
```bash
# PyForge automatically detects encoding
# If conversion fails, check verbose output for encoding issues
pyforge convert file.dbf --verbose
```

**Large Files**:
```bash
# Use compression to save space
pyforge convert large.dbf --compression gzip

# Monitor progress with verbose output
pyforge convert huge.dbf --verbose
```

**File Corruption**:
```bash
# Use verbose mode to see detailed error information
pyforge convert problematic.dbf --verbose

# Force overwrite if needed
pyforge convert data.dbf --force
```

## Validation and Inspection

### Pre-conversion Analysis

```bash
# Inspect DBF file structure
pyforge info legacy_data.dbf
```

Shows:
- Number of records
- Field definitions and types
- File size and format version
- Detected encoding
- Last modification date

### File Validation

```bash
# Check file integrity
pyforge validate suspicious.dbf

# Detailed validation with encoding check
pyforge validate file.dbf --check-encoding --verbose
```

## Performance Optimization

### Large File Processing

```bash
# Optimize for large DBF files
pyforge convert massive.dbf \
  --compression snappy \
  --verbose
```

### Batch Processing

```bash
# Convert multiple DBF files
for dbf_file in data/*.dbf; do
    echo "Converting: $dbf_file"
    pyforge convert "$dbf_file" \
      --compression gzip \
      --verbose
done
```

## Examples

### Legacy System Migration

```bash
# Convert old accounting system files
pyforge convert accounts.dbf \
  --compression gzip \
  --verbose

# Output includes automatic encoding detection and conversion details
```

### Geographic Data Processing

```bash
# Convert GIS shapefile DBF components
pyforge convert shapefile_attributes.dbf \
  --compression snappy

# Automatic encoding detection maintains data integrity
```

### Historical Data Recovery

```bash
# Recover data from potentially corrupted files
pyforge convert old_backup.dbf \
  --verbose \
  --force

# Review verbose output for data quality assessment
```

### International Data Handling

```bash
# Handle international character sets (automatic detection)
pyforge convert european_data.dbf --verbose
pyforge convert russian_data.dbf --verbose  
pyforge convert japanese_data.dbf --verbose
```

## Integration Examples

### Python/Pandas

```python
import pandas as pd

# Read converted DBF data
df = pd.read_parquet('converted_data.parquet')

# Convert string columns to appropriate types
def convert_dbf_types(df):
    for col in df.columns:
        # Clean string data (remove padding spaces)
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip()
        
        # Try to convert to numeric (will stay string if not possible)
        df[col] = pd.to_numeric(df[col], errors='ignore')
        
        # Try to convert to datetime (will stay string if not possible)
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except:
                pass
        
        # Convert boolean strings
        if df[col].dtype == 'object':
            bool_mask = df[col].isin(['true', 'false'])
            if bool_mask.any():
                df.loc[bool_mask, col] = df.loc[bool_mask, col].map({'true': True, 'false': False})
    return df

# Apply type conversion
df = convert_dbf_types(df)

# Data analysis with proper types
print(f"Records: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"Data types after conversion:\n{df.dtypes}")

# Now you can perform numeric operations on converted columns
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
if len(numeric_cols) > 0:
    print(f"Numeric summary:\n{df[numeric_cols].describe()}")
```

### Data Quality Assessment

```python
# Check for encoding issues
def check_encoding_quality(df):
    issues = []
    
    for col in df.select_dtypes(include=['object']).columns:
        # Check for replacement characters
        if df[col].str.contains('�', na=False).any():
            issues.append(f"Encoding issues in column: {col}")
    
    return issues

# Usage after conversion
df = pd.read_parquet('converted_file.parquet')
quality_issues = check_encoding_quality(df)
if quality_issues:
    print("Potential encoding problems:")
    for issue in quality_issues:
        print(f"  - {issue}")
```

### Spark Integration

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim

spark = SparkSession.builder.appName("DBFData").getOrCreate()

# Read converted parquet file
df = spark.read.parquet('converted_data.parquet')

# Clean typical DBF data issues
# Remove padding from string columns
string_columns = [field.name for field in df.schema.fields 
                 if field.dataType.typeName() == 'string']

for col_name in string_columns:
    df = df.withColumn(col_name, trim(col(col_name)))

# Show results
df.show(20)
```

## Troubleshooting

### Common Problems

**"File appears corrupted"**:
```bash
# Use verbose mode to see detailed error information
pyforge convert damaged.dbf --verbose

# Force overwrite to retry conversion
pyforge convert damaged.dbf --force --verbose
```

**"Garbled text in output"**:
- Encoding detection failed - check verbose output
- Use `pyforge info file.dbf` to verify file structure
- File may be corrupted or non-standard format

**"Out of memory errors"**:
```bash
# Use compression to reduce memory usage
pyforge convert large.dbf --compression gzip

# Monitor memory usage with verbose output
pyforge convert huge.dbf --verbose
```

### Debug Mode

```bash
# Get detailed processing information
pyforge convert file.dbf --verbose
```

This shows:
- Encoding detection process
- Field type mapping decisions
- Conversion progress
- Performance metrics

## Best Practices

1. **Backup Originals**: Keep original DBF files as backup
2. **Test Encoding**: Use `pyforge info` to check detected encoding
3. **Validate Results**: Compare record counts before/after conversion
4. **Handle Errors Gracefully**: Use `--skip-errors` for problematic files
5. **Use Compression**: GZIP compression saves significant space
6. **Batch Process**: Convert multiple files using shell scripts
7. **Check Data Quality**: Inspect converted data for encoding issues

## Legacy System Notes

### dBASE Variants

Different dBASE implementations may have slight variations:
- **Clipper**: May use different date formats
- **FoxPro**: Extended field types and sizes
- **Xbase++**: Modern extensions to DBF format

### Historical Context

DBF files were commonly used in:
- **1980s-1990s**: Primary database format for PC applications
- **GIS Systems**: Shapefile attribute tables
- **Legacy ERP**: Accounting and inventory systems
- **Point of Sale**: Retail transaction systems

## Character Encoding Reference

Common encodings for DBF files by region:

| Region | Encoding | Description |
|--------|----------|-------------|
| **US/Western Europe** | cp437, cp850 | DOS codepages |
| **Windows Systems** | cp1252 | Windows Latin-1 |
| **Eastern Europe** | cp852, iso-8859-2 | Central European |
| **Russian/Cyrillic** | cp866, cp1251 | Cyrillic encodings |
| **Modern Systems** | utf-8 | Unicode standard |

For complete command options and advanced features, see the [CLI Reference](../reference/cli-reference.md).
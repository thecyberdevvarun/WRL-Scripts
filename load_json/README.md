# JSON to SQL Server Importer

A Python script that reads manufacturing event data from a JSON file, transforms it into the required database schema, and bulk inserts the records into a Microsoft SQL Server table.

## Features

- Reads manufacturing event data from a JSON file
- Transforms JSON fields to match the SQL Server table structure
- Supports nested JSON objects (e.g., shift information)
- Uses `pyodbc` with `fast_executemany` for high-performance bulk inserts
- Automatically populates the synchronization timestamp (`SyncedAt`)
- Handles missing numeric values with default values
- Simple configuration through variables at the top of the script

---

## Requirements

- Python 3.8+
- Microsoft SQL Server
- ODBC Driver 17 for SQL Server

### Python Package

Install the required package:

```bash
pip install pyodbc
```

---

## Configuration

Update the configuration section in the script before running.

```python
SERVER = "YOUR_SQL_SERVER"
DATABASE = "YOUR_DATABASE"
USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"

FILE_PATH = r"path\to\your\json_file.json"
TABLE_NAME = "PartProcessEvents"
```

---

## Expected JSON Format

The script expects a JSON file with the following structure:

```json
{
    "date": "2026-06-04",
    "records": [
        {
            "event_id": "12345",
            "event_type": "Production",
            "barcode": "ABC123",
            "start_time": "08:00",
            "end_time": "08:30",
            "duration": "30",
            "parts_quantity": 100,
            "parts_quality": "Good",
            "operator_name": "John",
            "downtime_reason": null,
            "downtime_comment": null,
            "asset_name": "Machine-1",
            "line_name": "Line-A",
            "energy": 12.5,
            "shift": {
                "shift_name": "Morning"
            }
        }
    ]
}
```

---

## SQL Table Structure

The destination table should contain the following columns:

| Column | Type |
|---------|------|
| EventId | nvarchar |
| EventDate | date |
| ShiftName | nvarchar |
| EventType | nvarchar |
| Barcode | nvarchar |
| StartTime | nvarchar |
| EndTime | nvarchar |
| Duration | nvarchar |
| PartsQty | int |
| PartsQuality | nvarchar |
| OperatorName | nvarchar |
| DowntimeReason | nvarchar |
| DowntimeComment | nvarchar |
| AssetName | nvarchar |
| LineName | nvarchar |
| Energy | float |
| SyncedAt | datetime |

---

## How It Works

1. Connects to the SQL Server database.
2. Reads the JSON file.
3. Extracts the root date.
4. Iterates through each record.
5. Transforms the JSON fields into SQL table columns.
6. Performs a bulk insert using `executemany()`.
7. Commits the transaction.
8. Closes the database connection.

---

## Running the Script

```bash
python import_json.py
```

Example output:

```
Processing file: D:\Data\2026-06-04.json
Total records: 1250
DONE ✔
```

---

## Default Value Handling

If a field is missing, the script applies the following defaults:

| Field | Default |
|---------|----------|
| parts_quantity | 0 |
| energy | 0.0 |
| event_id | Empty string |
| SyncedAt | Current timestamp |

---

## Performance

The script uses:

- `cursor.fast_executemany = True`
- Bulk insert with `executemany()`

This significantly improves insertion performance for large datasets.

---

## Error Handling

The current version assumes:

- The JSON file is valid.
- The SQL Server connection is available.
- The destination table already exists.
- Column names match the script.

For production environments, consider adding:

- Try/except blocks
- Transaction rollback
- Logging
- Duplicate record detection
- Configuration via environment variables

---

## Project Structure

```
load_json/
│
├── load_file.py
├── README.md
└── json_output/
    └── 2026-06-04.json
```

---

## Notes

- Ensure the SQL Server ODBC Driver 17 is installed.
- The destination table must exist before running the script.
- `EventDate` is taken from the root `date` field in the JSON.
- `SyncedAt` is automatically set to the current system timestamp during import.

---

## License

This project is provided as-is for internal data import and automation purposes.

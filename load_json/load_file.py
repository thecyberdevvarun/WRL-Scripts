import json
import pyodbc
from datetime import datetime

# =========================
# CONFIG
# =========================
SERVER = "SERVER_IP"
DATABASE = "DB_NAME"
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"

FILE_PATH = r"JSON_FILE_PATH"
TABLE_NAME = "TABLE_NAME"

# =========================
# DB CONNECTION
# =========================
conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD}"
)

cursor = conn.cursor()
cursor.fast_executemany = True


# =========================
# TRANSFORM (MATCH TABLE)
# =========================
def transform_record(root_date, record):
    shift = record.get("shift", {})

    return (
        str(record.get("event_id") or ""),                 # EventId (nvarchar)
        root_date,                                          # EventDate (date)
        shift.get("shift_name"),                           # ShiftName
        record.get("event_type"),                          # EventType
        record.get("barcode"),                             # Barcode
        record.get("start_time"),                          # StartTime (nvarchar)
        record.get("end_time"),                            # EndTime (nvarchar)
        record.get("duration"),                            # Duration (nvarchar)

        int(record.get("parts_quantity") or 0),            # PartsQty (NOT NULL int)

        record.get("parts_quality"),                       # PartsQuality
        record.get("operator_name"),                       # OperatorName
        record.get("downtime_reason"),                     # DowntimeReason
        record.get("downtime_comment"),                    # DowntimeComment

        record.get("asset_name"),                          # AssetName
        record.get("line_name"),                           # LineName

        float(record.get("energy") or 0),                  # Energy (NOT NULL float)

        datetime.now()                                     # SyncedAt
    )


# =========================
# READ FILE
# =========================
def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    root_date = data.get("date")
    records = data.get("records", [])

    return [transform_record(root_date, r) for r in records]


# =========================
# INSERT DATA
# =========================
def insert_data(rows):
    if not rows:
        print("No data found")
        return

    query = f"""
    INSERT INTO {TABLE_NAME}
    (
        EventId,
        EventDate,
        ShiftName,
        EventType,
        Barcode,
        StartTime,
        EndTime,
        Duration,
        PartsQty,
        PartsQuality,
        OperatorName,
        DowntimeReason,
        DowntimeComment,
        AssetName,
        LineName,
        Energy,
        SyncedAt
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.executemany(query, rows)
    conn.commit()


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print(f"Processing file: {FILE_PATH}")

    rows = process_file(FILE_PATH)

    print(f"Total records: {len(rows)}")

    insert_data(rows)

    print("DONE ✔")

    cursor.close()
    conn.close()
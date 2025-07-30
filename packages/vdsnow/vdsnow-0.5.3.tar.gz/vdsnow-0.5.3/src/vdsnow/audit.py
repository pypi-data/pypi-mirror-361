import json
from typing import Dict, Any

# Let's define the audit table structure as constants
AUDIT_SCHEMA = "VDSNOW_INTERNAL"
AUDIT_TABLE = "VDSNOW_AUDIT_LOG"
QUALIFIED_AUDIT_TABLE = f"{AUDIT_SCHEMA}.{AUDIT_TABLE}"

def get_create_audit_infra_sql() -> str:
    """
    Returns the SQL commands to ensure the audit schema and table exist.
    This is idempotent and safe to run every time.
    """
    return f"""
        CREATE SCHEMA IF NOT EXISTS {AUDIT_SCHEMA};
        CREATE TABLE IF NOT EXISTS {QUALIFIED_AUDIT_TABLE} (
            RUN_AT TIMESTAMP_LTZ,
            ENVIRONMENT VARCHAR,
            AUDIT_DATA VARIANT
        );
    """


def get_insert_sql(audit_record: Dict[str, Any]) -> str:
    """
    Takes a Python dictionary, converts it to a JSON string, and returns
    the full SQL INSERT statement to log it.
    """
    # Convert the dictionary to a compact JSON string.
    # json.dumps automatically handles escaping characters.
    json_string = json.dumps(audit_record)

    # We need to escape single quotes within the JSON string for the SQL query
    escaped_json_string = json_string.replace("'", "''")

    # The environment is also a string that needs quotes
    environment = audit_record.get("env", "unknown")

    return f"""
        INSERT INTO {QUALIFIED_AUDIT_TABLE} (RUN_AT, ENVIRONMENT, AUDIT_DATA)
        SELECT
            CURRENT_TIMESTAMP(),
            '{environment}',
            PARSE_JSON('{escaped_json_string}')
        ;
    """

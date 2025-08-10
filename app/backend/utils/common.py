from __future__ import annotations


def to_bool(value):
    """Convert various value types to boolean integer (1/0), handling string 'true'/'false' from API"""
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    v = str(value).strip().lower()
    if v in {"true", "1", "yes"}:
        return 1
    if v in {"false", "0", "no"}:
        return 0
    return None

def safe_float(value):
    """Safely convert to float, handling string numbers and null values from API"""
    if value is None or value == "null" or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_int(value):
    """Safely convert to int, handling string numbers and null values from API"""
    if value is None or value == "null" or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None



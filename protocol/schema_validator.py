import json
from typing import Any, Dict, Tuple


def validate_json_schema(data: Dict[str, Any], required_fields: list[str]) -> Tuple[bool, str]:
    """Validates that output contains all required fields and is structural valid."""
    missing = [field for field in required_fields if field not in data]
    if missing:
        return False, f"Missing required fields: {missing}"
    return True, "OK"

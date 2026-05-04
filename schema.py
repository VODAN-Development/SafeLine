import uuid
from datetime import datetime

def generate_incident_id():
    return f"INC-{str(uuid.uuid4())[:8].upper()}"

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# Centralized Data Schema matching the new structure
SCHEMA = {
    "incident_id": {"type": str, "required": True, "default": generate_incident_id},
    "org_id": {"type": str, "required": False, "default": ""},
    "input_by": {"type": str, "required": False, "default": ""},
    "date_received": {"type": str, "required": False, "default": get_current_date},
    "date_recorded": {"type": str, "required": False, "default": get_current_date},
    
    # Location
    "country": {"type": str, "required": False, "default": ""},
    "state": {"type": str, "required": False, "default": ""},
    "town": {"type": str, "required": False, "default": ""},
    "village": {"type": str, "required": False, "default": ""},
    "camp": {"type": str, "required": False, "default": ""},
    "latitude": {"type": float, "required": False, "default": None},
    "longitude": {"type": float, "required": False, "default": None},
    
    # Incident Details
    "incident_date": {"type": str, "required": True, "default": ""},
    "incident_time_range": {
        "type": str, "required": False, "default": "Unknown",
        "choices": ["Morning", "Afternoon", "Evening", "Night", "Unknown"]
    },
    "violence_type": {
        "type": str, "required": True, "default": "Other",
        "choices": ["Rape", "Sexual Assault", "Physical Harassment", "Verbal Harassment", "Domestic Violence", "Other"]
    },
    "short_desc": {"type": str, "required": False, "default": ""},
    
    # Victim Details
    "num_victims": {"type": int, "required": False, "default": 1},
    "victim_age": {"type": int, "required": False, "default": None},
    "victim_gender": {
        "type": str, "required": False, "default": "Unknown",
        "choices": ["Female", "Male", "Non-binary", "Unknown"]
    },
    
    # Perpetrator Details
    "num_perpetrators": {"type": int, "required": False, "default": None},
    "perp_affiliation": {"type": str, "required": False, "default": ""},
    
    # Source / Publication Details
    "pub_type": {"type": str, "required": False, "default": ""},
    "pub_date": {"type": str, "required": False, "default": ""},
    "pub_link": {"type": str, "required": False, "default": ""}
}

def validate_and_transform(form_data):
    """
    Validates the incoming form dictionary against the SCHEMA.
    Returns: (validated_dict, list_of_errors)
    """
    validated = {}
    errors = []

    for field, rules in SCHEMA.items():
        raw_value = form_data.get(field, "").strip()

        # Handle empty/missing values
        if not raw_value:
            if rules.get("required"):
                if "default" in rules:
                    val = rules["default"]() if callable(rules["default"]) else rules["default"]
                    if val:
                        validated[field] = val
                        continue
                errors.append(f"{field} is required.")
                continue
            else:
                val = rules.get("default")
                validated[field] = val() if callable(val) else val
                continue

        # Type casting based on schema
        try:
            if rules["type"] == int:
                validated[field] = int(raw_value)
            elif rules["type"] == float:
                validated[field] = float(raw_value)
            else:
                validated[field] = str(raw_value)
        except ValueError:
            errors.append(f"Invalid format for {field}. Expected {rules['type'].__name__}.")
            continue

        # Controlled Values validation
        if "choices" in rules and validated[field] not in rules["choices"]:
            errors.append(f"{field} must be one of: {', '.join(rules['choices'])}.")

    return validated, errors
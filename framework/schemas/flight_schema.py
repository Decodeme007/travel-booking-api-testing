FLIGHT_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "flight_number": {"type": "string"},
        "airline": {"type": "string"},
        "origin": {"type": "string", "minLength": 3, "maxLength": 3},
        "destination": {"type": "string", "minLength": 3, "maxLength": 3},
        "departure_date": {"type": "string"},
        "departure_time": {"type": "string"},
        "arrival_time": {"type": "string"},
        "price": {"type": "number", "minimum": 0},
        "available_seats": {"type": "integer", "minimum": 0}
    },
    "required": [
        "id", "flight_number", "airline", "origin", "destination",
        "departure_date", "departure_time", "arrival_time", "price", "available_seats"
    ],
    "additionalProperties": False
}

FLIGHT_SEARCH_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "total_flights": {"type": "integer", "minimum": 0},
        "flights": {
            "type": "array",
            "items": FLIGHT_ITEM_SCHEMA
        }
    },
    "required": ["total_flights", "flights"],
    "additionalProperties": False
}

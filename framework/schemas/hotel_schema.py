HOTEL_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "city": {"type": "string"},
        "address": {"type": "string"},
        "rating": {"type": "number", "minimum": 0, "maximum": 5},
        "price_per_night": {"type": "number", "minimum": 0},
        "available_rooms": {"type": "integer", "minimum": 0}
    },
    "required": [
        "id", "name", "city", "address", "rating", "price_per_night", "available_rooms"
    ],
    "additionalProperties": False
}

HOTEL_SEARCH_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "total_hotels": {"type": "integer", "minimum": 0},
        "hotels": {
            "type": "array",
            "items": HOTEL_ITEM_SCHEMA
        }
    },
    "required": ["total_hotels", "hotels"],
    "additionalProperties": False
}

BOOKING_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "booking_reference": {"type": "string"},
        "user_id": {"type": "integer"},
        "booking_type": {"type": "string", "enum": ["FLIGHT", "HOTEL"]},
        "item_id": {"type": "integer"},
        "passengers_or_guests": {"type": "integer", "minimum": 1},
        "total_price": {"type": "number", "minimum": 0},
        "status": {"type": "string", "enum": ["PENDING", "CONFIRMED", "CANCELLED"]},
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"}
    },
    "required": [
        "id", "booking_reference", "user_id", "booking_type", "item_id",
        "passengers_or_guests", "total_price", "status", "created_at", "updated_at"
    ],
    "additionalProperties": False
}

BOOKING_STATUS_SCHEMA = {
    "type": "object",
    "properties": {
        "booking_id": {"type": "integer"},
        "booking_reference": {"type": "string"},
        "status": {"type": "string"},
        "booking_type": {"type": "string"},
        "total_price": {"type": "number"},
        "payment_status": {"type": ["string", "null"]},
        "cancellation_status": {"type": ["string", "null"]}
    },
    "required": ["booking_id", "booking_reference", "status", "booking_type", "total_price"],
    "additionalProperties": False
}

CANCELLATION_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "cancellation_id": {"type": "integer"},
        "booking_id": {"type": "integer"},
        "cancellation_reason": {"type": "string"},
        "refund_amount": {"type": "number", "minimum": 0},
        "refund_status": {"type": "string"},
        "cancelled_at": {"type": "string"},
        "booking_status": {"type": "string", "enum": ["CANCELLED"]}
    },
    "required": [
        "cancellation_id", "booking_id", "cancellation_reason",
        "refund_amount", "refund_status", "cancelled_at", "booking_status"
    ],
    "additionalProperties": False
}

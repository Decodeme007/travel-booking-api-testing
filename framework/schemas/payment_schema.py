PAYMENT_SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "payment_id": {"type": "integer"},
        "payment_reference": {"type": "string"},
        "booking_id": {"type": "integer"},
        "amount": {"type": "number", "minimum": 0},
        "currency": {"type": "string"},
        "payment_method": {"type": "string"},
        "status": {"type": "string", "enum": ["SUCCESS", "FAILED"]},
        "transaction_date": {"type": "string"},
        "failure_reason": {"type": ["string", "null"]}
    },
    "required": [
        "payment_id", "payment_reference", "booking_id",
        "amount", "currency", "payment_method", "status", "transaction_date"
    ],
    "additionalProperties": False
}

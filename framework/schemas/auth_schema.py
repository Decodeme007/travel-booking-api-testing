LOGIN_SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "access_token": {"type": "string", "minLength": 10},
        "token_type": {"type": "string", "enum": ["bearer"]},
        "expires_in": {"type": "integer", "minimum": 1},
        "user_id": {"type": "integer"},
        "username": {"type": "string"},
        "role": {"type": "string"}
    },
    "required": ["access_token", "token_type", "expires_in", "user_id", "username", "role"],
    "additionalProperties": False
}

USER_PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "email": {"type": "string"},
        "role": {"type": "string"},
        "created_at": {"type": "string"}
    },
    "required": ["id", "username", "email", "role", "created_at"],
    "additionalProperties": False
}

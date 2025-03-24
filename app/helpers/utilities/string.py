def to_string(value: int | float) -> str | None:
    try:
        string_value = str(value)
        return string_value
    except ValueError:
        return None

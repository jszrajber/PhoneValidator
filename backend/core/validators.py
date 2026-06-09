"""
File for pydantic validators
"""


def number_validator(number: str) -> str:
    number = number.strip()

    if not number or len(number) > 16 or len(number) < 8:
        raise ValueError("Valid number should contain between 8 to 16 characters")

    try:
        int(number.lstrip("+"))

    except ValueError:
        raise ValueError("Number should not contain any letters")

    return number

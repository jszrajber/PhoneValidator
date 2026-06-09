from pydantic import BaseModel, Field, field_validator
from backend.core.validators import number_validator


class NumberCheck(BaseModel):
    number: str = Field(..., min_length=8, max_length=16)

    @field_validator("number")
    @classmethod    # Sprawdz blad bez tego
    def validate_number(cls, v: str):
        return number_validator(v)
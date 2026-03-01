from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional


class Registration(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    name: str
    phone_number: Optional[str] = None
    datetime: str

class CreateRegistration(BaseModel):
    email: Optional[EmailStr] = None
    name: str
    phone_number: Optional[str] = None

    @model_validator(mode='before')
    def at_least_one_contact(cls, values):
        email = values.get('email')
        phone = values.get('phone_number')
        if not email and not phone:
            raise ValueError('Provide at least email or phone_number')
        return values
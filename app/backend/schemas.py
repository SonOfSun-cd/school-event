from pydantic import BaseModel, EmailStr


class Registration(BaseModel):
    id: int
    email: EmailStr
    name: str
    phone_number: str
    datetime: str

class CreateRegistration(BaseModel):
    email: EmailStr
    name: str
    phone_number: str
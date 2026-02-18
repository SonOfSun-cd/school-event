from pydantic import BaseModel, EmailStr


class Registration(BaseModel):
    id: int
    email: EmailStr
    name: str
    surname: str

class CreateRegistration(BaseModel):
    email: EmailStr
    name: str
    surname: str
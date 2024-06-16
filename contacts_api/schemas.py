from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class ContactModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birth_date: date
    additional_info: Optional[str] = None

class ContactResponse(ContactModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birth_date: date
    additional_info: Optional[str] = None

class ContactCreate(ContactModel):
    pass

class ContactUpdate(ContactModel):
    pass 

class ContactDelete(ContactModel):
    pass

class ContactInDB(ContactModel):
    id: int

    class Config:
        orm_mode = True
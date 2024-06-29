from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
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

class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    email: EmailStr
    password: str = Field(min_length=5, max_length=15)

class UserDB(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    user: UserDB
    detail: str = 'User succesfully created'

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class RequestEmail(BaseModel):
    email: EmailStr
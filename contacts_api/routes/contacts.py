from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from contacts_api.database.db import get_db
from contacts_api.schemas import ContactModel, ContactInDB
from contacts_api.repository import contacts as repository_contacts
from contacts_api.routes.auth import auth_service
from contacts_api.database.models import User

router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get('/', response_model=List[ContactInDB])
async def read_contacts(skip: int = 0, limit: int = 5, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts

@router.get('/{contact_id}', response_model=ContactInDB)
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact

@router.get('/{query}', response_model=List[ContactInDB])
async def find_contact(query: str, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.find_contact(query, current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts found')
    return contacts

@router.post('/', response_model=ContactInDB)
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.create_contact(body, current_user, db)

@router.put('/{contact_id}', response_model=ContactInDB)
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get('/contacts/upcoming_birthdays', response_model=List[ContactInDB])
async def get_birthdays(db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    birthdays = await repository_contacts.get_birthdays(current_user, db)
    if birthdays is None:
        return "No birtdays this week"
    return birthdays

@router.delete('{contact_id}', response_model=ContactInDB)
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
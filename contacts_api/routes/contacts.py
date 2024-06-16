from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from contacts_api.database.db import get_db
from contacts_api.schemas import ContactModel, ContactInDB
from contacts_api.repository import contacts as repository_contacts

router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get('/', response_model=List[ContactInDB])
async def read_contacts(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    return contacts

@router.get('/{contact_id}', response_model=ContactInDB)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact

@router.get('/{query}', response_model=List[ContactInDB])
async def find_contact(query: str, db: Session = Depends(get_db)):
    contacts = await repository_contacts.find_contact(query, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts found')
    return contacts

@router.post('/', response_model=ContactInDB)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body, db)

@router.put('/{contact_id}', response_model=ContactInDB)
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get('/contacts/upcoming_birthdays', response_model=List[ContactInDB])
async def get_birthdays(db: Session = Depends(get_db)):
    birthdays = await repository_contacts.get_birthdays(db)
    if birthdays is None:
        return "No birtdays this week"
    return birthdays

@router.delete('{contact_id}', response_model=ContactInDB)
async def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
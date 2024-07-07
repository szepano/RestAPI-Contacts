from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from contacts_api.database.db import get_db
from contacts_api.schemas import ContactModel, ContactInDB
from contacts_api.repository import contacts as repository_contacts
from contacts_api.routes.auth import auth_service
from contacts_api.database.models import User

router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get('/', response_model=List[ContactInDB], description='No more than 10 requests pre minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 5, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve contacts with rate limiting (10 requests per minute).

    :param skip: Number of records to skip.
    :type skip: int
    :param limit: Maximum number of records to retrieve.
    :type limit: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :raises HTTPException 404: If contacts not found.
    :return: List of contacts.
    :rtype: List[ContactInDB]
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts

@router.get('/{contact_id}', response_model=ContactInDB, description='No more than 10 requests pre minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a contact by ID with rate limiting (10 requests per minute).

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :raises HTTPException 404: If contact not found.
    :return: Retrieved contact.
    :rtype: ContactInDB
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    return contact

@router.get('/{query}', response_model=List[ContactInDB], description='No more than 10 requests pre minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def find_contact(query: str, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Find contacts by query with rate limiting (10 requests per minute).

    :param query: The search query.
    :type query: str
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :raises HTTPException 404: If no contacts found.
    :return: List of matching contacts.
    :rtype: List[ContactInDB]
    """
    contacts = await repository_contacts.find_contact(query, current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts found')
    return contacts

@router.post('/', response_model=ContactInDB, description='No more than 10 requests pre minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Create a new contact with rate limiting (10 requests per minute).

    :param body: The contact details to create.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: Created contact.
    :rtype: ContactInDB
    """
    return await repository_contacts.create_contact(body, current_user, db)

@router.put('/{contact_id}', response_model=ContactInDB, description='No more than 10 requests pre minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Update a contact by ID with rate limiting (10 requests per minute).

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated contact details.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :raises HTTPException 404: If contact not found.
    :return: Updated contact.
    :rtype: ContactInDB
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get('/contacts/upcoming_birthdays', response_model=List[ContactInDB], description='No more than 10 requests pre minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_birthdays(db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve upcoming birthdays with rate limiting (10 requests per minute).

    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: List of contacts with upcoming birthdays.
    :rtype: List[ContactInDB]
    """
    birthdays = await repository_contacts.get_birthdays(current_user, db)
    if birthdays is None:
        return "No birtdays this week"
    return birthdays

@router.delete('{contact_id}', response_model=ContactInDB, description='No more than 10 requests pre minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Delete a contact by ID with rate limiting (10 requests per minute).

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :raises HTTPException 404: If contact not found.
    :return: Deleted contact.
    :rtype: ContactInDB
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
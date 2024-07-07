from typing import List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import extract, and_

from contacts_api.database.models import Contact, User
from contacts_api.schemas import ContactModel

async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """returns every contact saved by current user

    :param skip: how many contacts will be skipped
    :type skip: int
    :param limit: max number of contacts displayed on one page
    :type limit: int
    :param user: current user
    :type user: User
    :param db: database session
    :type db: Session
    :return: contacts saved in db by this user
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()

async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """Searches for a record by it's index

    :param contact_id: searched index
    :type contact_id: int
    :param user: current user
    :type user: User
    :param db: database session
    :type db: Session
    :return: contact with given index
    :rtype: Contact
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

async def find_contact(query: str, user: User, db: Session) -> List[Contact] | None:
    """Searches for a contact by sequence of characters in email, last name or first name.

    :param query: sequence used to search through database
    :type query: str
    :param user: current user
    :type user: User
    :param db: database session
    :type db: Session
    :return: matching records if found
    :rtype: List[Contact] | None
    """
    contacts = db.query(Contact).filter(
        (Contact.user_id == user.id) & 
        (
        (Contact.first_name.ilike(f'%{query}%')) |
        (Contact.last_name.ilike(f'%{query}%')) |
        (Contact.email.ilike(f'%{query}%'))
        )
    ).all()
    if contacts == []:
        return None
    else:
        return contacts

async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """Creates and saves contact in database

    :param body: Contact instance with all the needed parameters
    :type body: ContactModel
    :param user: current user
    :type user: User
    :param db: database session
    :type db: Session
    :return: Contact that is being saved
    :rtype: Contact
    """
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def update_contact(contact_id: int, body: ContactModel, user: User, db: Session) -> Contact | None:
    """Updates an existing contact in database

    :param contact_id: index of already existing contact
    :type contact_id: int
    :param body: new instance of contact to save
    :type body: ContactModel
    :param user: current user
    :type user: User
    :param db: database session
    :type db: Session
    :return: newly saved contact
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birth_date = body.birth_date
        contact.additional_info = body.additional_info
        db.commit()
    return contact

async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """Removes a contact from database

    :param contact_id: index of contact to remove
    :type contact_id: int
    :param user: current user
    :type user: User
    :param db: database session
    :type db: Session
    :return: contact that is being removed
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

async def get_birthdays(user: User, db: Session) -> List[Contact] | None:
    """Checks who from saved contacts has birthday in a week

    :param user: current user
    :type user: User
    :param db: database session
    :type db: Session
    :return: all contacts that have birthday in a week
    :rtype: List[Contact] | None
    """
    today = datetime.today().date()
    today_month = today.month
    today_day = today.day

    next_week = today + timedelta(days=7)
    next_week_month = next_week.month
    next_week_day = next_week.day

    if today_month == next_week_month:
        result =  db.query(Contact).filter(
            Contact.user_id == user.id,
            extract('month', Contact.birth_date) == today_month,
            extract('day', Contact.birth_date).between(today_day, next_week_day)
            ).all()
    
    else:
        result = db.query(Contact).filter(
            Contact.user_id == user.id,
            (extract('month', Contact.birth_date) == today_month) & (extract('day', Contact.birth_date) >= today_day) |
            (extract('month', Contact.birth_date) == next_week_month) & (extract('day', Contact.birth_date) <= next_week_day)
        ).all()
    if result != []:
        return result
    else:
        return result
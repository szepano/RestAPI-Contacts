from typing import List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import extract, and_

from contacts_api.database.models import Contact, User
from contacts_api.schemas import ContactModel

async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()

async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

async def find_contact(query: str, user: User, db: Session) -> List[Contact]:
    contacts = db.query(Contact).filter(
        (Contact.user_id == user.id) & 
        (
        (Contact.first_name.ilike(f'%{query}%')) |
        (Contact.last_name.ilike(f'%{query}%')) |
        (Contact.email.ilike(f'%{query}%'))
        )
    ).all()
    return contacts

async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def update_contact(contact_id: int, body: ContactModel, user: User, db: Session) -> Contact | None:
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
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

async def get_birthdays(user: User, db: Session):
    today = datetime.today().date()
    today_month = today.month
    today_day = today.day

    next_week = today + timedelta(days=7)
    next_week_month = next_week.month
    next_week_day = next_week.day

    if today_month == next_week_month:
        return db.query(Contact).filter(
            Contact.user_id == user.id,
            extract('month', Contact.birth_date) == today_month,
            extract('day', Contact.birth_date).between(today_day, next_week_day)
            ).all()
    
    else:
        return db.query(Contact).filter(
            Contact.user_id == user.id,
            (extract('month', Contact.birth_date) == today_month) & (extract('day', Contact.birth_date) >= today_day) |
            (extract('month', Contact.birth_date) == next_week_month) & (extract('day', Contact.birth_date) <= next_week_day)
        ).all()
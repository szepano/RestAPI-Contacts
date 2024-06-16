from typing import List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import extract

from contacts_api.database.models import Contact
from contacts_api.schemas import ContactModel

async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    return db.query(Contact).offset(skip).limit(limit).all()

async def get_contact(contact_id: int, db: Session) -> Contact:
    return db.query(Contact).filter(Contact.id == contact_id).first()

async def find_contact(query: str, db: Session) -> List[Contact]:
    contacts = db.query(Contact).filter(
        (Contact.first_name.ilike(f'%{query}%')) |
        (Contact.last_name.ilike(f'%{query}%')) |
        (Contact.email.ilike(f'%{query}%'))
    ).all()
    return contacts

async def create_contact(body: ContactModel, db: Session) -> Contact:
    contact = Contact(**body.dict())
    # contact = Contact(
    #     first_name = body.first_name,
    #     last_name = body.last_name,
    #     email = body.email,
    #     phone = body.phone,
    #     birth_date = body.birth_date,
    #     additional_info = body.additional_info
    # )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def update_contact(contact_id: int, body: ContactModel, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birth_date = body.birth_date
        contact.additional_info = body.additional_info
        db.commit()
    return contact

async def remove_contact(contact_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

async def get_birthdays(db: Session):
    today = datetime.today().date()
    today_month = today.month
    today_day = today.day

    next_week = today + timedelta(days=7)
    next_week_month = next_week.month
    next_week_day = next_week.day

    if today_month == next_week_month:
        return db.query(Contact).filter(
            extract('month', Contact.birth_date) == today_month,
            extract('day', Contact.birth_date).between(today_day, next_week_day)
            ).all()
    
    else:
        return db.query(Contact).filter(
            (extract('month', Contact.birth_date) == today_month) & (extract('day', Contact.birth_date) >= today_day) |
            (extract('month', Contact.birth_date) == next_week_month) & (extract('day', Contact.birth_date) <= next_week_day)
        ).all()
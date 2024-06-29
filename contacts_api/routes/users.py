from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from contacts_api.database.db import get_db
from contacts_api.database.models import User
from contacts_api.repository import users as repository_users
from contacts_api.services.auth import auth_service
from contacts_api.conf.config import settings
from contacts_api.schemas import UserDB

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/me/', response_model=UserDB)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user
    
  
@router.patch('/avatar', response_model=UserDB)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'ContactsApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactsApp/{current_user.username}').build_url(width=250, height=250, crop='fill', version=r.get('version'))

    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user


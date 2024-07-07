from sqlalchemy.orm import Session
from contacts_api.database.models import User
from contacts_api.schemas import UserModel

async def get_user_by_email(email: str, db: Session) -> User:
    """Searches for an user in database by email

    :param email: email searched in database
    :type email: str
    :param db: database session
    :type db: Session
    :return: user with searched email
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates an user

    :param body: Data for the user to create.
    :type body: UserModel
    :param db: database session.
    :type db: Session
    :return: Newly created user.
    :rtype: User
    """
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a user.

    :param user: The user whose token is being updated.
    :type user: User
    :param token: The new refresh token. Can be None to remove the token.
    :type token: Optional[str]
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm a user's email address.

    :param email: The email address to confirm.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update the avatar URL for a user.

    :param email: The email address of the user whose avatar is being updated.
    :type email: str
    :param url: The new avatar URL.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: The updated user object.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
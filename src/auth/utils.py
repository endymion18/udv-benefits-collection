import secrets
import smtplib
import uuid
from email.message import EmailMessage

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pygments.lexer import default
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from src.admin.models import UserInfoView, UserInfoTable
from src.auth.exceptions import WrongEmail, NotVerified, NotActive, InvalidToken
from src.auth.models import User, AuthToken
from src.config import SECRET_KEY, EMAIL_FROM, EMAIL_PASS, SERVER_HOSTNAME
from src.database import get_session

security = HTTPBearer()


async def verify_user(email: str, session: AsyncSession):
    user_from_db = await session.exec(select(User).where(User.email == email))
    user_from_db = user_from_db.first()

    if user_from_db is None:
        raise WrongEmail("This user does not exist")

    if not user_from_db.email_verified:
        raise NotActive("This user is not verified")

    if not user_from_db.active_user:
        raise NotVerified("This user is not active")

    return user_from_db.id


async def encode_jwt_token(data: dict):
    jwt_token = jwt.encode(data, SECRET_KEY, "HS256")
    return jwt_token


async def generate_auth_link(user_id: uuid.UUID, session: AsyncSession):
    token = secrets.token_urlsafe(20)
    auth_token = AuthToken(token=token, user_id=user_id)
    session.add(auth_token)
    await session.commit()
    return f"{SERVER_HOSTNAME}/users/authorize/{token}"


async def verify_auth_token(token: str, session: AsyncSession):
    auth_token = await session.exec(select(AuthToken).where(AuthToken.token == token))
    auth_token = auth_token.first()
    if auth_token is None:
        raise InvalidToken("Ссылка для входа недействительна")
    jwt_token = await encode_jwt_token({"sub": auth_token.user_id.__str__()})
    user = await session.exec(select(User).where(User.id == auth_token.user_id))
    user = user.first()
    if user.email_verified is False:
        user.email_verified = True
    session.add(user)
    await session.delete(auth_token)
    await session.commit()

    return {"success": jwt_token}


async def send_email(email_to: str, message: str, msg_type: str = None, invite_from: str = None):
    msg = EmailMessage()
    msg['From'] = EMAIL_FROM
    msg['To'] = email_to
    match msg_type:
        case 'login':
            msg['Subject'] = 'Логин в личный кабинет сервиса "Кафетерий бенефитов"'
            with open('./static/index.html') as html:
                text = html.read()
                text = text.replace('url-example', message)
        case 'invite':
            msg['Subject'] = 'Приглашение в "Кафетерий бенефитов"'
            with open('./static/invite.html') as html:
                text = html.read()
                text = text.replace('url-example', message)
                text = text.replace('ivanivanov@udv.ru', invite_from)
        case _:
            msg['Subject'] = 'Mail confirmation'
            text = ''

    msg.set_content(text, 'html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.send_message(msg)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                           session: AsyncSession = Depends(get_session)):
    decoded_token = jwt.decode(credentials.credentials, SECRET_KEY, ["HS256"])
    user_id = decoded_token.get("sub")
    user = await session.exec(select(User).where(User.id == user_id))
    user = user.first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.active_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is deleted")
    return user


async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security),
                            session: AsyncSession = Depends(get_session)):
    user = await get_current_user(credentials, session)
    if user.role_id == 1:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Access denied")


async def get_profile(session: AsyncSession, user: User):
    user_instance = await session.exec(select(User, UserInfoTable).join(UserInfoTable).
                                       where(User.active_user == True).
                                       where(User.id == user.id))

    user_instance = user_instance.first()

    if user_instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user, user_info = user_instance

    user_info_view = UserInfoView(
        user_uuid=user.id,
        email=user.email,
        full_name=user_info.full_name,
        place_of_employment=user_info.place_of_employment,
        position=user_info.position,
        employment_date=user_info.employment_date,
        administration=user.role_id,
    )

    return user_info_view

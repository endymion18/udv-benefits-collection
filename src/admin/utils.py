import sqlalchemy
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from src.admin.models import UserInfoTable, UserInfoView, UserInfo
from src.auth.models import User
from src.auth.utils import send_email, generate_auth_link


async def get_users(session: AsyncSession):
    users = await session.exec(select(User, UserInfoTable).join(UserInfoTable).where(User.active_user == True))
    users = users.fetchall()
    users = [UserInfoView(
        user_uuid=user.id,
        email=user.email,
        full_name=user_info.full_name,
        place_of_employment=user_info.place_of_employment,
        position=user_info.position,
        employment_date=user_info.employment_date,
        administration=user.role_id,
    ) for user, user_info in users]
    return users


async def get_user(uuid: str, session: AsyncSession):
    user_instance = await session.exec(select(User, UserInfoTable).join(UserInfoTable).
                                       where(User.active_user == True).
                                       where(User.id == uuid))

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


async def update_user_info(uuid: str, user_info: UserInfo, session: AsyncSession):
    user_instance = await session.exec(select(User, UserInfoTable).join(UserInfoTable).
                                       where(User.active_user == True).
                                       where(User.id == uuid))
    user_instance = user_instance.first()
    if user_instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_db, user_info_db = user_instance
    update_data = user_info.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(user_info_db, key):
            setattr(user_info_db, key, value)
    if update_data['administration']:
        user_db.role_id = 1
    else:
        user_db.role_id = 2
    session.add(user_info_db)
    session.add(user_db)
    await session.commit()
    return UserInfoView(
        user_uuid=user_db.id,
        email=user_db.email,
        full_name=user_info_db.full_name,
        place_of_employment=user_info_db.place_of_employment,
        position=user_info_db.position,
        employment_date=user_info_db.employment_date,
        administration=user_db.role_id,
    )


async def make_user_inactive(uuid: str, session: AsyncSession):
    user = await session.exec(select(User).where(User.id == uuid))
    user = user.first()
    user.active_user = False
    session.add(user)
    await session.commit()
    return {"success": f"User {user.email} is deleted"}


async def add_user(user_info: UserInfo, session: AsyncSession, email_from: str):
    try:
        role_id = 1 if user_info.administration else 2
        user = User(email=user_info.email, active_user=True, role_id=role_id)
        session.add(user)
        await session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with email {user_info.email} already exists")
    # send email
    auth_link = await generate_auth_link(user.id, session)
    await send_email(user_info.email, auth_link, 'invite', email_from)
    user_info_table = UserInfoTable(user_id=user.id, **user_info.model_dump())
    session.add(user_info_table)
    await session.commit()
    return {"success": f"Message has been sent to {user_info.email}"}

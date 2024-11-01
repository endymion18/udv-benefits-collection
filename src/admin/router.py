from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.admin.models import UserInfo
from src.admin.utils import get_users, get_user, update_user_info, make_user_inactive, add_user
from src.auth.models import User
from src.auth.utils import get_current_admin
from src.database import get_session

router = APIRouter(prefix="/admin",
                   tags=["Users"])


@router.get("/users")
async def get_all_users(session: AsyncSession = Depends(get_session), admin: User = Depends(get_current_admin)):
    users = await get_users(session)
    return users


@router.post("/users/add")
async def add_new_user(user_info: UserInfo, session: AsyncSession = Depends(get_session),
                       admin: User = Depends(get_current_admin)):
    return await add_user(user_info, session, admin.email)


@router.get("/users/{uuid}")
async def get_user_by_uuid(uuid: str, session: AsyncSession = Depends(get_session),
                           admin: User = Depends(get_current_admin)):
    user_info = await get_user(uuid, session)
    return user_info


@router.put("/users/{uuid}")
async def update_user_by_uuid(uuid: str, user_info: UserInfo,
                              session: AsyncSession = Depends(get_session),
                              admin: User = Depends(get_current_admin)):
    updated_user_info = await update_user_info(uuid, user_info, session)
    return updated_user_info


@router.delete("/users/{uuid}")
async def remove_user_by_uuid(uuid: str,
                              session: AsyncSession = Depends(get_session),
                              admin: User = Depends(get_current_admin)):
    return await make_user_inactive(uuid, session)

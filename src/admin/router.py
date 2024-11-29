from pathlib import Path

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import FileResponse

from src.admin.models import UserInfo
from src.admin.utils import get_users, get_user, update_user_info, make_user_inactive, add_user
from src.auth.models import User
from src.auth.utils import get_current_admin, get_current_user
from src.benefit_requests.utils import get_all_requests, change_request_status, get_request_info_by_id
from src.database import get_session

project_root = Path(__file__).resolve().parents[2]
files_path = project_root / "files/receipts"

router = APIRouter(prefix="/admin",
                   tags=["Admin"])


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


@router.get("/requests")
async def get_all_benefit_requests(sort_by_date_desc: bool = True, session: AsyncSession = Depends(get_session),
                                   admin: User = Depends(get_current_admin)):
    return await get_all_requests(sort_by_date_desc, session)


@router.get("/requests/{request_id}")
async def get_request_info(request_id: int, session: AsyncSession = Depends(get_session),
                           admin: User = Depends(get_current_admin)):
    return await get_request_info_by_id(request_id, session)


@router.get("/requests/{request_id}/{path}")
async def get_request_file(path: str):
    img_path = Path(files_path / path)
    return FileResponse(img_path)


@router.put("/requests/{request_id}/apply")
async def apply_request(request_id: int, session: AsyncSession = Depends(get_session),
                        admin: User = Depends(get_current_admin)):
    return await change_request_status(request_id, 2, session)


@router.put("/requests/{request_id}/deny")
async def deny_request(request_id: int, session: AsyncSession = Depends(get_session),
                       admin: User = Depends(get_current_admin)):
    return await change_request_status(request_id, 3, session)

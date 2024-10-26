from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.analitycs.models import PollSchema
from src.analitycs.utils import get_current_poll_status, set_current_poll_status, add_poll_results
from src.auth.models import User
from src.auth.utils import get_current_admin, get_current_user
from src.database import get_session

router = APIRouter(prefix="/analytics",
                   tags=["Analytics"])


@router.get("/poll-status")
async def get_poll_status(session: AsyncSession = Depends(get_session), admin: User = Depends(get_current_admin)):
    return await get_current_poll_status(session)


@router.put("/poll-status/set")
async def set_poll_status(status: bool, session: AsyncSession = Depends(get_session),
                          admin: User = Depends(get_current_admin)):
    return await set_current_poll_status(status, session)


@router.post("/poll")
async def take_poll(poll_data: PollSchema, session: AsyncSession = Depends(get_session),
                    user: User = Depends(get_current_user)):
    return await add_poll_results(poll_data, str(user.id), session)



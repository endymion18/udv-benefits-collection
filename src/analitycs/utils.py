from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from src.analitycs.models import PollStatus, PollSchema, PollResults
from src.benefits.models import Benefit


async def get_current_poll_status(session: AsyncSession):
    poll_status = await session.exec(select(PollStatus))
    poll_status = poll_status.first()

    return {"is_poll_active": poll_status.status}


async def set_current_poll_status(new_status: bool, session: AsyncSession):
    poll_status = await session.exec(select(PollStatus))
    poll_status = poll_status.first()
    poll_status.status = new_status
    session.add(poll_status)
    await session.commit()
    # if new_status = true send message to all users

    return {"is_poll_active": poll_status.status}


async def add_poll_results(poll_data: PollSchema, user_id: str, session: AsyncSession):
    await validate_poll_results(poll_data, session)
    poll_results = PollResults(user_id=user_id, **poll_data.model_dump())
    session.add(poll_results)
    await session.commit()
    return poll_results


async def validate_poll_results(poll_data: PollSchema, session: AsyncSession):
    poll_status = await get_current_poll_status(session)
    if not poll_status["is_poll_active"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Poll is currently inactive")
    if poll_data.satisfaction_rate < 0 or poll_data.satisfaction_rate > 5:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid satisfaction_rate")

    benefits_ids = await session.exec(select(Benefit.id))
    benefits_ids = benefits_ids.all()
    for benefit in poll_data.selected_benefits:
        if benefit not in benefits_ids:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid benefit id")

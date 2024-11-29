from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from src.analitycs.models import PollStatus, PollSchema, PollResults
from src.auth.models import User
from src.benefit_requests.models import UserBenefitRelation
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


async def get_analytics(session: AsyncSession):
    employees = await session.exec(select(User).where(User.active_user and User.email_verified))
    employees = employees.all()
    if len(employees) == 0:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail="No employees yet")
    benefit_users = set()

    benefits = await session.exec(select(Benefit))
    benefits = benefits.all()
    benefits_dict = {}
    for benefit in benefits:
        benefits_dict[benefit.name] = {
            "Ожидает": 0,
            "Одобрено": 0,
            "Отказано": 0
        }

    requests = await session.exec(
        select(UserBenefitRelation, Benefit).join(Benefit, Benefit.id == UserBenefitRelation.benefit_id))
    requests = requests.all()

    requests_approved = 0
    requests_denied = 0
    requests_waiting = 0

    for request, benefit in requests:
        benefit_users.add(request.user_id)
        match request.status:
            case 1:
                requests_waiting += 1
                benefits_dict[benefit.name]["Ожидает"] += 1
            case 2:
                requests_approved += 1
                benefits_dict[benefit.name]["Одобрено"] += 1
            case 3:
                requests_denied += 1
                benefits_dict[benefit.name]["Отказано"] += 1

    benefit_users_count = len(benefit_users)
    employees_count = len(employees)

    usage_percent = round(benefit_users_count * 100 / employees_count, 2)

    total_requests = requests_approved + requests_waiting + requests_denied

    return {
        "бенефиты": benefits_dict,
        "заявки_ожидает": requests_waiting,
        "заявки_завершена": requests_approved,
        "заявки_отклонена": requests_denied,
        "заявки_всего": total_requests,
        "пользуются_бенефитами": benefit_users_count,
        "все_сотрудники": employees_count,
        "соотношение_использования": usage_percent
    }

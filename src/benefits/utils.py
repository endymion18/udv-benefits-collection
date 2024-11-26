import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from src.admin.models import UserInfoTable
from src.auth.models import User
from src.benefits.models import Benefit, BenefitBase, BenefitShort, Category
from src.config import SERVER_URL

project_root = Path(__file__).resolve().parents[2]
files_path = project_root / "files/benefit_covers"


async def add_benefit(benefit_data: BenefitBase, session: AsyncSession):
    benefit = Benefit(**benefit_data.model_dump())
    session.add(benefit)
    await session.commit()
    return benefit


async def get_benefits(user_data: User, session: AsyncSession):
    benefits = await session.exec(select(Benefit))
    benefits = benefits.all()
    benefits = await filter_benefits(user_data, benefits, session)
    benefits = [BenefitShort(benefit.id, benefit.name, benefit.card_name, benefit.cover_path) for benefit in benefits]

    return benefits


async def get_benefit(benefit_id: int, session: AsyncSession):
    benefit = await session.exec(select(Benefit).where(Benefit.id == benefit_id))
    benefit = benefit.first()
    if benefit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Benefit with id {benefit_id} not found")
    return benefit


async def delete_benefit(benefit_id: int, session: AsyncSession):
    benefit = await get_benefit(benefit_id, session)
    await update_cover(benefit.id, None, session)
    await session.delete(benefit)
    await session.commit()


async def update_cover(benefit_id: int, image: UploadFile | None, session: AsyncSession):
    benefit = await get_benefit(benefit_id, session)
    try:
        if benefit.cover_path is not None:
            os.remove(files_path / benefit.cover_path)
    except FileNotFoundError as e:
        print(e)

    if image is not None:
        image_id = uuid.uuid4()
        ext = os.path.splitext(image.filename)[1]
        image_path = f"{image_id}.{ext}"
        with open(files_path / image_path, "wb") as uploaded_file:
            file_content = await image.read()
            uploaded_file.write(file_content)

        benefit.cover_path = image_path

        session.add(benefit)
        await session.commit()

        return f"{SERVER_URL}/benefits/images/{image_path}"


async def update_benefit(benefit_id: int, benefit_data: BenefitBase, session: AsyncSession):
    benefit = await get_benefit(benefit_id, session)
    update_data = benefit_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(benefit, key, value)
    session.add(benefit)
    await session.commit()
    return BenefitShort(benefit_id, benefit.name, benefit.card_name, benefit.cover_path)


async def get_categories(session: AsyncSession):
    categories = await session.exec(select(Category))
    categories = categories.all()
    print(categories)
    return categories


async def filter_benefits(user, benefits, session):
    if user.role_id == 1:
        return benefits
    else:
        filtered_benefits = []
        categories = await get_categories(session)
        user_instance = await session.exec(select(User, UserInfoTable).join(UserInfoTable).
                                           where(User.active_user == True).
                                           where(User.id == user.id))
        user_instance = user_instance.first()
        worker_exp_days = (datetime.now().date() - user_instance[1].employment_date).days
        for benefit in benefits:
            for category in benefit.categories:
                if category == 1:
                    filtered_benefits.append(benefit)
                    break
                elif category in [2, 3]:
                    if categories[category - 2].availability_interval.days < worker_exp_days:
                        filtered_benefits.append(benefit)
                        break
                elif category == 4:
                    if categories[3].availability_interval.days < worker_exp_days:
                        filtered_benefits.append(benefit)

        return filtered_benefits

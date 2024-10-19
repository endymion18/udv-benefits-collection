import os
import uuid

from fastapi import HTTPException, UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from src.benefits.models import Benefit, BenefitBase, BenefitShort, Category
from src.config import SERVER_HOSTNAME


async def add_benefit(benefit_data: BenefitBase, session: AsyncSession):
    benefit = Benefit(**benefit_data.model_dump())
    session.add(benefit)
    await session.commit()
    return benefit


async def get_benefits(session: AsyncSession):
    benefits = await session.exec(select(Benefit))
    benefits = benefits.all()
    benefits = [BenefitShort(benefit.name, benefit.card_name, benefit.cover_path) for benefit in benefits]

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
    os.chdir(".")
    benefit = await get_benefit(benefit_id, session)
    try:
        if benefit.cover_path is not None:
            os.remove(f"files/benefit_covers/{benefit.cover_path}")
    except FileNotFoundError as e:
        print(e)

    if image is not None:
        image_id = uuid.uuid4()
        ext = os.path.splitext(image.filename)[1]
        image_path = f"{image_id}.{ext}"

        with open(f"files/benefit_covers/{image_path}", "wb") as uploaded_file:
            file_content = await image.read()
            uploaded_file.write(file_content)

        benefit.cover_path = image_path

        session.add(benefit)
        await session.commit()

        return f"{SERVER_HOSTNAME}/benefits/images/{image_path}"


async def update_benefit(benefit_id: int, benefit_data: BenefitBase, session: AsyncSession):
    benefit = await get_benefit(benefit_id, session)
    update_data = benefit_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(benefit, key, value)
    session.add(benefit)
    await session.commit()
    return BenefitShort(benefit.name, benefit.card_name, benefit.cover_path)


async def get_categories(session: AsyncSession):
    categories = await session.exec(select(Category))
    categories = categories.all()
    print(categories)
    return categories

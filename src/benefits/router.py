import os
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import FileResponse

from src.auth.models import User
from src.auth.utils import get_current_user, get_current_admin
from src.benefits.models import Benefit, BenefitBase
from src.benefits.utils import add_benefit, get_benefits, get_benefit, delete_benefit, update_benefit, update_cover
from src.database import get_session

router = APIRouter(prefix="/benefits",
                   tags=["Benefits"])


@router.get("/all")
async def get_all_benefits(session: AsyncSession = Depends(get_session),
                           user_data: User = Depends(get_current_user)):
    benefits = await get_benefits(session)
    return benefits


@router.post("/new")
async def add_new_benefit(benefit: BenefitBase,
                          session: AsyncSession = Depends(get_session),
                          admin: User = Depends(get_current_admin)):
    benefit = await add_benefit(benefit, session)
    return {"success": benefit}


@router.get("/{benefit_id}")
async def get_benefit_info_by_id(benefit_id: int,
                                 session: AsyncSession = Depends(get_session),
                                 admin: User = Depends(get_current_admin)):
    benefit = await get_benefit(benefit_id, session)
    return benefit


@router.post("/{benefit_id}/cover")
async def update_benefit_cover(benefit_id: int, image: UploadFile | None,
                               session: AsyncSession = Depends(get_session),
                               admin: User = Depends(get_current_admin)):
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File type not allowed. Only images are accepted.")
    url = await update_cover(benefit_id, image, session)
    return {"success": url}


@router.put("/edit/{benefit_id}")
async def edit_benefit_by_id(benefit_id: int,
                             benefit: BenefitBase,
                             session: AsyncSession = Depends(get_session),
                             admin: User = Depends(get_current_admin)):
    updated_benefit = await update_benefit(benefit_id, benefit, session)
    return updated_benefit


@router.delete("/delete/{benefit_id}")
async def delete_benefit_by_id(benefit_id: int,
                               session: AsyncSession = Depends(get_session),
                               admin: User = Depends(get_current_admin)):
    await delete_benefit(benefit_id, session)
    return {"success": f"benefit with id {benefit_id} has been deleted"}


@router.get("/images/{path}")
async def get_benefit_cover(path: str):
    os.chdir(".")
    img_path = Path(f"files/benefit_covers/{path}")
    return FileResponse(img_path)

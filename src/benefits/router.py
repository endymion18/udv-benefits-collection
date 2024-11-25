import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, HTTPException, File
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import FileResponse

from src.auth.models import User
from src.auth.utils import get_current_user, get_current_admin
from src.benefits.models import BenefitBase
from src.benefits.utils import add_benefit, get_benefits, get_benefit, delete_benefit, update_benefit, update_cover, \
    get_categories, validate_benefit_request
from src.database import get_session

router = APIRouter(prefix="/benefits",
                   tags=["Benefits"])

project_root = Path(__file__).resolve().parents[2]
files_path = project_root / "files/benefit_covers"


@router.get("/all")
async def get_all_benefits(session: AsyncSession = Depends(get_session),
                           user_data: User = Depends(get_current_user)):
    benefits = await get_benefits(user_data, session)
    return benefits


@router.get("/categories")
async def get_all_categories(session: AsyncSession = Depends(get_session),
                             admin: User = Depends(get_current_admin)):
    categories = await get_categories(session)
    return categories


@router.post("/new")
async def add_new_benefit(benefit: BenefitBase,
                          session: AsyncSession = Depends(get_session),
                          admin: User = Depends(get_current_admin)):
    benefit = await add_benefit(benefit, session)
    return {"success": benefit}


@router.get("/{benefit_id}")
async def get_benefit_info_by_id(benefit_id: int,
                                 session: AsyncSession = Depends(get_session),
                                 admin: User = Depends(get_current_user)):
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
    img_path = Path(files_path / path)
    return FileResponse(img_path)


@router.post("/apply/{benefit_id}")
async def apply_benefit(benefit_id: int, session: AsyncSession = Depends(get_session),
                        user: User = Depends(get_current_user), files: list[UploadFile | str] = None):
    if len(files) != 0:
        files = None if isinstance(files[0], str) else files
    return await validate_benefit_request(benefit_id, files, session, user)

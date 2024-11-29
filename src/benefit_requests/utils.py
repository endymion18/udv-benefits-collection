import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from src.admin.models import UserInfoTable
from src.auth.models import User
from src.benefits.models import Benefit
from src.benefit_requests.models import UserBenefitRelation, BenefitStatuses
from src.benefits.utils import get_benefit, files_path
from src.config import SERVER_URL

project_root = Path(__file__).resolve().parents[2]
receipts_path = project_root / "files/receipts"


async def validate_benefit_request(benefit_id: int, files: list[UploadFile] | None, session: AsyncSession,
                                   user: User):
    file_paths = None
    benefit = await get_benefit(benefit_id, session)

    if not benefit.need_confirmation:
        return None

    if not benefit.need_files:
        files = None

    if files is not None:
        if len(files) > 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Too much files")
        for file in files:
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400,
                                    detail=f"{file.filename} file type not allowed. Only images are accepted.")
            if file.size > 20000000:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"File {file.filename} is too large")
        file_paths = await upload_files(benefit_id, files)
    user_benefit_relation = UserBenefitRelation(user_id=user.id,
                                                benefit_id=benefit.id,
                                                files=file_paths,
                                                status=1)
    session.add(user_benefit_relation)
    await session.commit()

    return {"detail": "Benefit request successfully created"}


async def upload_files(benefit_id: int, files: list[UploadFile]):
    file_paths = []
    for image in files:
        image_id = uuid.uuid4()
        ext = os.path.splitext(image.filename)[1]
        image_path = f"{image_id}_{benefit_id}.{ext}"
        with open(receipts_path / image_path, "wb") as uploaded_file:
            file_content = await image.read()
            uploaded_file.write(file_content)

        file_paths.append(image_path)

    return file_paths


async def get_user_requests_by_id(user_id: uuid.UUID, session: AsyncSession):
    requests = await session.exec(select(UserBenefitRelation, Benefit, BenefitStatuses).where(
        UserBenefitRelation.user_id == user_id).join(
        BenefitStatuses, UserBenefitRelation.status == BenefitStatuses.id).join(
        Benefit, UserBenefitRelation.benefit_id == Benefit.id).order_by(UserBenefitRelation.created_at.desc()))
    requests = requests.all()
    if len(requests) == 0:
        return None
    else:
        request_list = []
        for request in requests:
            relation, benefit, benefit_status = request
            request_list.append({
                "request_id": relation.id,
                "name": benefit.name,
                "creation_date": relation.created_at,
                "status": f"Заявка {benefit_status.name}"
            })
    return request_list


async def get_all_requests(sort_by_date_desc: bool, session: AsyncSession):
    sort_column = UserBenefitRelation.created_at.desc() if sort_by_date_desc else UserBenefitRelation.created_at
    requests = await session.exec(
        select(UserBenefitRelation, Benefit, BenefitStatuses,
               UserInfoTable).join(BenefitStatuses,
                                   UserBenefitRelation.status == BenefitStatuses.id).join(
            Benefit, UserBenefitRelation.benefit_id == Benefit.id).join(
            UserInfoTable, UserInfoTable.user_id == UserBenefitRelation.user_id).order_by(
            sort_column))
    requests = requests.all()
    if len(requests) == 0:
        return None
    else:
        request_list = []
        for request in requests:
            relation, benefit, benefit_status, user_info = request
            request_list.append({
                "request_id": relation.id,
                "name": benefit.name,
                "user_name": user_info.full_name,
                "creation_date": relation.created_at,
                "status": f"Заявка {benefit_status.name}"
            })
    return request_list


async def change_request_status(request_id: int, request_status: int, session: AsyncSession):
    statuses = await session.exec(select(BenefitStatuses))
    statuses = statuses.all()
    request = await session.exec(select(UserBenefitRelation).where(UserBenefitRelation.id == request_id))
    request = request.first()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Request with id {request_id} is not found")
    else:
        request.status = request_status
        session.add(request)
        await session.commit()
        return {"detail": f"Заявка {statuses[request_status - 1].name}"}


async def get_request_info_by_id(request_id: int, session: AsyncSession):
    request = await session.exec(
        select(UserBenefitRelation, Benefit, BenefitStatuses,
               UserInfoTable).join(BenefitStatuses,
                                   UserBenefitRelation.status == BenefitStatuses.id).join(
            Benefit, UserBenefitRelation.benefit_id == Benefit.id).join(
            UserInfoTable, UserInfoTable.user_id == UserBenefitRelation.user_id).where(
            UserBenefitRelation.id == request_id))
    request = request.first()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Request with id {request_id} is not found")
    else:
        relation, benefit, benefit_status, user_info = request
        files = []
        if relation.files is not None:
            for path in relation.files:
                files.append(f"{SERVER_URL}/admin/requests/{request_id}/{path}" if path is not None else None)
        request_info = {
            "request_id": relation.id,
            "name": benefit.name,
            "user_name": user_info.full_name,
            "creation_date": relation.created_at,
            "status": f"Заявка {benefit_status.name}",
            "attached_files": files
        }
    return request_info


async def validate_insurance_request(benefit_id: int, insurance_member: str, insurance_type: str,
                                     files: list[UploadFile], session: AsyncSession,
                                     user: User):
    file_paths = None
    benefit = await get_benefit(benefit_id, session)
    if files is not None:
        if len(files) > 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Too much files")
        for file in files:
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400,
                                    detail=f"{file.filename} file type not allowed. Only images are accepted.")
            if file.size > 20000000:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"File {file.filename} is too large")
        file_paths = await upload_files(benefit_id, files)
    user_benefit_relation = UserBenefitRelation(user_id=user.id,
                                                benefit_id=benefit.id,
                                                files=file_paths,
                                                status=1,
                                                additional_info=[insurance_member, insurance_type])
    session.add(user_benefit_relation)
    await session.commit()

    return {"detail": "Benefit request successfully created"}

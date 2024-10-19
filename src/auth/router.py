from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from src.auth.exceptions import WrongEmail, NotVerified, NotActive, InvalidToken
from src.auth.models import UserBase, User
from src.auth.utils import verify_user, send_email, generate_auth_link, verify_auth_token, get_current_user, \
    get_current_admin
from src.database import get_session

router = APIRouter(tags=["Auth"], prefix="/users")


@router.post("/login",
             status_code=status.HTTP_200_OK
             )
async def login(user_data: UserBase,
                session: AsyncSession = Depends(get_session)):
    email = user_data.email
    try:
        user_uuid = await verify_user(email, session)
    except (WrongEmail, NotVerified, NotActive) as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)
    auth_link = await generate_auth_link(user_uuid, session)
    await send_email(email, auth_link)

    return {"success": f"Ссылка для входа отправлена на {email}"}


@router.get("/authorize/{token}",
            status_code=status.HTTP_200_OK
            )
async def authorize(token: str, session: AsyncSession = Depends(get_session)):
    try:
        jwt_token = await verify_auth_token(token, session)
    except InvalidToken as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)

    return jwt_token

import datetime
import uuid
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    email: str = Field(max_length=320, unique=True, index=True, nullable=False)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email_verified: bool = Field(default=False)
    active_user: bool = Field(default=False)
    role_id: int = Field(foreign_key="role.id")


class Role(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=25, nullable=False)


class AuthToken(SQLModel, table=True):
    __tablename__ = "auth_token"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(max_length=40, nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    create_date: datetime.datetime | None = Field(default_factory=datetime.datetime.now)

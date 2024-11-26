import datetime
import uuid

from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import SQLModel, Field, Column, String


class BenefitStatuses(SQLModel, table=True):
    __tablename__ = "benefit_statuses"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=30, nullable=False)


class UserBenefitRelation(SQLModel, table=True):
    __tablename__ = "user_benefit_relation"

    id: int | None = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    benefit_id: int = Field(foreign_key="benefit.id")
    created_at: datetime.datetime | None = Field(default_factory=datetime.datetime.now)
    files: list[str] = Field(sa_column=Column(ARRAY(String), nullable=True), default=None)
    status: int = Field(foreign_key="benefit_statuses.id")
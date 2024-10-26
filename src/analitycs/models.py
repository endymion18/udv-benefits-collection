import datetime
import uuid

from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import SQLModel, Field, Column, Integer


class PollStatus(SQLModel, table=True):
    __tablename__ = "poll_status"

    status: bool = Field(default=False, primary_key=True)


class PollResults(SQLModel, table=True):
    __tablename__ = "poll_results"

    id: int | None = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    create_date: datetime.datetime | None = Field(default_factory=datetime.datetime.now)
    selected_benefits: list[int] | None = Field(sa_column=Column(ARRAY(Integer), nullable=True), default=None)
    satisfaction_rate: int


class PollSchema(BaseModel):
    selected_benefits: list[int]
    satisfaction_rate: int

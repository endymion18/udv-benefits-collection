from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import SQLModel, Field, Column, Integer
from sqlalchemy import Interval

from src.config import SERVER_HOSTNAME


class BenefitBase(SQLModel):
    name: str = Field(max_length=80, nullable=False)
    card_name: str = Field(max_length=80, nullable=True)
    text: str = Field(nullable=True)
    categories: list[int] = Field(sa_column=Column(ARRAY(Integer), nullable=True))


class Benefit(BenefitBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    cover_path: str = Field(max_length=150, nullable=True)


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=30, nullable=False)
    availability_interval: str = Field(sa_column=Column(Interval, nullable=True))


class BenefitShort:
    name: str
    card_name: str
    cover_url: str

    def __init__(self, name, card_name, cover_path):
        self.name = name
        self.card_name = card_name
        self.cover_url = f"{SERVER_HOSTNAME}/benefits/images/{cover_path}" if cover_path is not None else None

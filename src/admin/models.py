import datetime

import pytz
from dateutil.relativedelta import relativedelta
import uuid

from sqlmodel import SQLModel, Field


class UserInfoBase(SQLModel):
    full_name: str | None = Field(max_length=100, nullable=True, default=None)
    place_of_employment: str | None = Field(max_length=150, nullable=True, default=None)
    position: str | None = Field(max_length=120, nullable=True, default=None)
    employment_date: datetime.date | None = Field(nullable=True, default=None)


class UserInfo(UserInfoBase):
    email: str = Field(max_length=320, unique=True, index=True, nullable=False)
    administration: bool | None = False


class UserInfoTable(UserInfoBase, table=True):
    __tablename__ = "user_info_table"
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class UserInfoView:
    user_uuid: uuid.UUID
    email: str
    full_name: str | None
    place_of_employment: str | None
    position: str | None
    employment_date: str | None
    administration: bool

    def __init__(self,
                 user_uuid: uuid.UUID,
                 email: str,
                 full_name: str = None,
                 place_of_employment: str = None,
                 position: str = None,
                 employment_date: datetime.date = None,
                 administration: int = 2):
        self.user_uuid = user_uuid
        self.email = email
        self.full_name = full_name
        self.place_of_employment = place_of_employment
        self.position = position
        self.employment_date = self._count_experience(employment_date)
        self.administration = True if administration == 1 else False

    @staticmethod
    def _count_experience(past_date):
        now = datetime.datetime.now()
        delta = relativedelta(now, past_date)

        if delta.years > 0:
            if delta.years % 10 == 1 and delta.years % 100 != 11:
                return f"{delta.years} год"
            elif 2 <= delta.years % 10 <= 4 and not (12 <= delta.years % 100 <= 14):
                return f"{delta.years} года"
            else:
                return f"{delta.years} лет"
        elif delta.months > 0:
            if delta.months % 10 == 1 and delta.months % 100 != 11:
                return f"{delta.months} месяц"
            elif 2 <= delta.months % 10 <= 4 and not (12 <= delta.months % 100 <= 14):
                return f"{delta.months} месяца"
            else:
                return f"{delta.months} месяцев"
        elif delta.days > 0:
            if delta.days % 10 == 1 and delta.days % 100 != 11:
                return f"{delta.days} день"
            elif 2 <= delta.days % 10 <= 4 and not (12 <= delta.days % 100 <= 14):
                return f"{delta.days} дня"
            else:
                return f"{delta.days} дней"
        else:
            return "1 день"

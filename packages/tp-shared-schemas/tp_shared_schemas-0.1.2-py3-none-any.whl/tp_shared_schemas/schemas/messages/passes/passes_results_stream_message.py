from datetime import date
from enum import Enum

from tp_helper import BaseSchema


class TimeOfDateType(str, Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"


class PassSeriesType(str, Enum):
    AA = "AA"
    BA = "БА"
    AB = "АБ"
    BB = "ББ"
    MB = "МБ"
    MK = "МК"
    MA = "МА"
    MO = "MO"


class AllowedZoneType(str, Enum):
    MKAD = "МКАД"
    SK = "СК"
    TTK = "ТТК"
    MO = "МО"


class PassesResultsMessageItem(BaseSchema):
    reg_number: str | None

    time_of_day: TimeOfDateType | None

    series: PassSeriesType | None
    number: str | None

    allowed_zone: AllowedZoneType | None

    start_date: date | None
    end_date: date | None
    cancel_date: date | None


class PassesResultsStreamMessageSchema(BaseSchema):
    reg_number: str
    passes: list[PassesResultsMessageItem] = []

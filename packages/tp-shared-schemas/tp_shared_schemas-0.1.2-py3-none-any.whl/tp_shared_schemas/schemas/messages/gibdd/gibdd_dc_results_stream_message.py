import enum
from datetime import date

from pydantic import ConfigDict
from tp_helper import BaseSchema


class GibddOperatorStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSE = "PAUSE"
    CANCEL = "CANCEL"


class GibddDcResultOperator(BaseSchema):
    operator_id: int
    status: GibddOperatorStatus
    name: str
    address_line: str
    phone_number: str
    email: str
    site: str
    canceled_date: date | None
    canceled_at: int | None


class GibddDcResultItem(BaseSchema):
    card_number: str
    vin: str
    start_date: date
    end_date: date
    odometer_value: int
    is_active: bool
    updated_at: int
    created_at: int

    operator: GibddDcResultOperator

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class GibddDcResultsStreamMessage(BaseSchema):
    vin: str
    diagnostic_cards: list[GibddDcResultItem] = []

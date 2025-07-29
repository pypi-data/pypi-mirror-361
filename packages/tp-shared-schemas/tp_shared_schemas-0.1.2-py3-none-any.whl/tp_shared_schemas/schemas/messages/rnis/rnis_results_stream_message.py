from tp_helper import BaseSchema


class RNISResultMessageSchema(BaseSchema):
    reg_number: str
    exists: bool
    last_mark: int | None
    terminals_amount: int

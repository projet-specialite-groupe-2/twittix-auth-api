from pydantic import BaseModel
from datetime import datetime


class token_is_valid_response(BaseModel):
    email: str
    token: str
    exp_time: datetime


class temporary_token_response(BaseModel):
    temporary_token: str

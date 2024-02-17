from typing import Optional

from pydantic import BaseModel


class Config(BaseModel):
    frequency: Optional[int] = None


class User(BaseModel):
    user_id: str
    username: str
    token: str
    config: Config = Config()

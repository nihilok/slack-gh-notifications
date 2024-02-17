from typing import Optional

from pydantic import BaseModel, ConfigDict

from notifications.models import Notification


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")
    frequency: Optional[int] = None


class User(BaseModel):
    user_id: str
    username: str
    token: str
    config: Config = Config()
    notifications: list[Notification] = []

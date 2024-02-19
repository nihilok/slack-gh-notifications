from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


@dataclass
class Comment:
    id: int
    body: str
    author: str
    html_url: str


class Notification(BaseModel):
    id: int
    slack_user_id: str
    repo: str
    title: str
    reason: str
    url: str
    updated_at: datetime
    thread_url: str
    latest_comment: Optional[Comment] = None

    def __gt__(self, other):
        if self.updated_at and other.updated_at:
            return self.updated_at > other.updated_at
        return self.id > other.id

    def __eq__(self, other):
        return self.id == other.id and self.updated_at == other.updated_at

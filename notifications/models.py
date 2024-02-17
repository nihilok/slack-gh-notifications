from dataclasses import dataclass
from typing import Optional


@dataclass
class Comment:
    id: str
    body: str
    author: str
    html_url: str


@dataclass
class Notification:
    id: str
    repo: str
    title: str
    reason: str
    url: str
    latest_comment: Optional[Comment] = None

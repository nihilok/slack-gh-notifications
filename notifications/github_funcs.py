import os
from typing import Optional

import requests
from requests import Response

from notifications.models import Notification, Comment

NOTIFICATIONS_URL = "https://api.github.com/notifications"


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_notifications(token: str) -> Response:
    return requests.get(
        NOTIFICATIONS_URL,
        headers=get_headers(token),
    )


def check_token(token: str) -> bool:
    return get_notifications(token).status_code == 200


class AuthenticationError(Exception):
    pass


def get_notifications_json(token: str) -> dict:
    response = get_notifications(token)
    if response.status_code == 401:
        raise AuthenticationError("Please refresh token")
    return response.json()


def build_notification_from_json(n: dict, token: str) -> Notification:
    latest_comment_url = n["subject"]["latest_comment_url"] or n["subject"]["url"]
    latest_comment = get_latest_comment(latest_comment_url, token)
    manual_url = (
        n["subject"]["url"]
        .replace("api.", "")
        .replace("repos/", "")
        .replace("pulls", "pull")
    )
    return Notification(
        n["id"],
        n["repository"]["full_name"],
        n["subject"]["title"],
        n["reason"],
        manual_url,
        latest_comment,
    )


def get_latest_comment(latest_comment_url, token) -> Optional[Comment]:
    latest_url_response = requests.get(
        latest_comment_url,
        headers=get_headers(token),
    )
    if latest_url_response.status_code != 200:
        return None
    else:
        latest_url = latest_url_response.json()
        latest_url = Comment(
            latest_url["id"],
            latest_url["body"],
            latest_url["user"]["login"],
            latest_url["html_url"],
        )
    return latest_url


def get_all_user_notifications(token: str) -> list[Notification]:

    notifications = get_notifications_json(token)
    return [build_notification_from_json(n, token) for n in notifications]


def get_unread_user_notifications(token: str) -> list[Notification]:
    notifications = get_notifications_json(token)
    return [build_notification_from_json(n, token) for n in notifications if n.unread]


if __name__ == "__main__":
    print(get_all_user_notifications(os.environ.get("GH_NOTIFICATIONS_TOKEN")))

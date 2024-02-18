import os

from slack_sdk import WebClient

from data.user import User
from notifications.models import Notification


def format_message(notification: Notification):
    url = (
        notification.url
        if not notification.latest_comment
        else notification.latest_comment.html_url
    )
    base_message = f"""*New Notification*
<{url}|{notification.title}> _({" ".join(notification.reason.split("_"))})_
"""
    if notification.latest_comment:
        comment = notification.latest_comment
        base_message += f"""
_*@{comment.author}* commented:_
"""
        for line in comment.body.split("\n"):
            base_message += f"\n> {line}"
    return base_message


def notify_slack(user: User, notification: Notification):
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    client.chat_postMessage(
        channel=user.user_id,
        text=format_message(notification),
        user=user.user_id,
        mrkdwn=True,
        unfurl_links=False,
    )

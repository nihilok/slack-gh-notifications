import os

from slack_sdk import WebClient

from data.user import User
from notifications.interactions import Interactions
from notifications.models import Notification


def get_blocks(notification: Notification, updated=False):
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{'New' if not updated else 'Updated'} notification",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<{notification.latest_comment.html_url if notification.latest_comment else notification.url}|{notification.title}>*",
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Reason:* {' '.join(notification.reason.split('_'))}",
                }
            ],
        },
    ]
    if (
        notification.latest_comment
        and notification.latest_comment.html_url != notification.url
    ):
        blocks.append(
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"_*@{notification.latest_comment.author}* commented:_",
                    }
                ],
            },
        )
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": notification.latest_comment.body,
                },
            },
        )
    blocks.append(
        {
            "type": "actions",
            "block_id": "unsubscribe-block",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Unsubscribe",
                        "emoji": True,
                    },
                    # The value string includes a reference to the callback and also the args
                    # to be passed to the callback e.g. `<CALLBACK_ID>::<ARG1>__<ARG2>__<ARG3>__etc..`
                    "value": f"{Interactions.UNSUBSCRIBE_THREAD.value}::{notification.slack_user_id}__{notification.thread_url}",
                    "action_id": "unsubscribe-thread-action",
                },
            ],
        },
    )
    return blocks


def notify_slack(user: User, notification: Notification, updated=False):
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    client.chat_postMessage(
        channel=user.user_id,
        user=user.user_id,
        mrkdwn=True,
        unfurl_links=False,
        blocks=get_blocks(notification, updated),
        text=f"{'Update on' if updated else 'New notification for'} {notification.title}",
    )

import json
import os
from enum import Enum

from flask import Response, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app import data_manager
from notifications.github_funcs import unsubscribe_thread

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))


class Interactions(Enum):
    UNSUBSCRIBE_THREAD = "unsubscribe_from_thread"


def get_event_payload() -> dict:
    payload_str = request.values.get("payload", "{}")
    return json.loads(payload_str)


def parse_args_from_callback_id(callback_id) -> tuple[str, tuple[str, ...]]:
    parts = callback_id.split("::")
    callback_id = parts[0]
    args = tuple(parts[1].split("__"))
    return callback_id, args


def unsubscribe_thread_callback(user_id, thread_url, payload: dict):
    message = payload.get("message", {})
    message_ts = message.get("ts")
    channel_id = payload.get("channel", {}).get("id")
    user = data_manager.get(user_id)
    if user is None:
        return Response("User not subscribed", status=404)

    if not unsubscribe_thread(user.token, thread_url):
        return Response("Something went wrong", status=400)

    # remove the actions block at the bottom of the message (removes the Unsubscribe button)
    existing_blocks = message.get("blocks")
    existing_blocks.pop()
    response = client.chat_update(
        channel=channel_id, ts=message_ts, blocks=existing_blocks
    )
    if response["ok"]:
        try:
            # add an emoji reaction to the message
            client.reactions_add(
                channel=channel_id, name="zipper_mouth_face", timestamp=response["ts"]
            )
        except SlackApiError as e:
            if "already_reacted" not in str(e):
                raise e
    return Response("Unsubscribed!", status=200)


EVENT_CALLBACKS = {Interactions.UNSUBSCRIBE_THREAD.value: unsubscribe_thread_callback}

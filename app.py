import os
from pathlib import Path

import requests
from flask import Flask, request, Response, abort
from pydantic import ValidationError
from slack_sdk import WebClient
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler

from data.sqlite_manager import SQLiteManager
from data.user import User, Config
from notifications.main_task import start_scheduler

app = Flask(__name__)
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
bolt_app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)

data_manager = SQLiteManager("./users.db")
start_scheduler(data_manager)


@bolt_app.message()
def greetings(payload: dict, say: Say):
    """Listens for the word "hello" in a Slack message and responds accordingly"""
    if "hello" in payload.get("text", "").lower():
        user = payload.get("user")
        say(f"Hi <@{user}>")


handler = SlackRequestHandler(bolt_app)


@app.route("/gh/events", methods=["POST"])
def slack_events():
    """Main events handler for events/messages from Slack"""
    return handler.handle(request)


def authenticate():
    """Verify that the request is genuinely coming from Slack"""
    if request.is_json:
        token = request.json.get("token")
    else:
        token = request.values.get("token")
    local = os.environ.get("VERIFICATION_TOKEN")
    if token != local:
        abort(403)
    return True


@app.before_request
def before_request():
    authenticate()


@app.route("/gh", methods=["GET"])
def index():
    """Used just to test authentication"""
    return Response("Hello World!", 200)


@app.route("/gh/subscribe", methods=["POST"])
def subscribe():
    """Subscribe user to GitHub notifications"""
    user_id = request.values["user_id"]
    gh_token = request.values["text"]
    authenticated = requests.get(
        "https://api.github.com/notifications",
        headers={
            "Authorization": f"Bearer {gh_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if authenticated.status_code != 200:
        # can't return a 401 here or Slack will think the request failed
        return Response("Invalid token", status=202)
    username = request.values["user_name"]
    data_manager.subscribe_user(
        User(user_id=user_id, username=username, token=gh_token)
    )
    return Response(f"You are now subscribed to GitHub notifications.", 200)


@app.route("/gh/config", methods=["POST"])
def config():
    """Subscribe user to GitHub notifications"""
    user_id = request.values["user_id"]
    try:
        kv_pairs = request.values["text"].split(" ")
        tuple_list = [
            (kv_pairs[i], kv_pairs[i + 1]) for i in range(0, len(kv_pairs), 2)
        ]
        config_update = dict(tuple_list)
        try:
            user = data_manager[user_id]
        except ValidationError:
            return Response(
                "Corrupted user data, please unsubscribe and resubscribe.",
                status=202,
            )
        except KeyError:
            return Response(
                "User is not subscribed. Please subscribe with GH notifications token.",
                status=202,
            )
        existing_config = user.config.model_dump()
        existing_config.update(config_update)
        user.config = Config(**existing_config)
        data_manager.save(user)
    except ValidationError as e:
        errors = e.errors()
        error_text = "ERROR: "
        for e in errors:
            error_text += f"{e['loc'][1]}: {e['msg']}\n"
        return Response(error_text, status=202)
    except IndexError:
        return Response(
            "ERROR: Unable to parse space separated key/value pairs from message.",
            status=202,
        )
    return Response(f"Config updated.", 200)


@app.route("/gh/unsubscribe", methods=["POST"])
def unsubscribe():
    """Unsubscribe user from GitHub notifications and delete all data"""
    user_id = request.values["user_id"]
    data_manager.unsubscribe_user(user_id)
    return Response(f"Unsubscribed", 200)


if __name__ == "__main__":
    app.run(port=7778, host="0.0.0.0", debug=True)

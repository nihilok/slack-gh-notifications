import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

""" We need to pass the 'Bot User OAuth Token' """
slack_token = os.environ.get('SLACK_BOT_TOKEN')

# Creating an instance of the Webclient class
client = WebClient(token=slack_token)

try:
    # Sending a message to a particular user
    response = client.chat_postEphemeral(
        channel="bot",
        text="Hello USERID0000",
        user="U06JNN7LGF8")

except SlackApiError as e:
    print(e.response["error"])

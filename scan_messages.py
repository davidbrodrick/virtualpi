#!/usr/bin/python3

import os
from slack_bolt import App
import json

#Create handle to Slack
app = App(token=os.environ["SLACK_BOT_TOKEN"])
bot_userid = os.environ["SLACK_BOT_USERID"]
channel_name = os.environ["SLACK_CHANNEL_NAME"]

save_to_file = "./bot_messages.json"

channel_id = None
# Call the conversations.list method using the WebClient
for result in app.client.conversations_list():
    if channel_id is not None:
        break
    for channel in result["channels"]:
        if channel["name"] == channel_name:
            channel_id = channel["id"]
            #Print result
            print(f"Found conversation ID: {channel_id}")
            break

if channel_id is None:
    raise ValueError(f"Unable to find channel named: {channel_name:s}")

# Store conversation history
conversation_history = []

# Call the conversations.history method using the WebClient
# conversations.history returns the first 100 messages by default
# These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
result = app.client.conversations_history(channel=channel_id)
while True:
    conversation_history += result["messages"]
    if not result.data["has_more"]:
        break
    cursor = result.data["response_metadata"]["next_cursor"]
    result = app.client.conversations_history(channel=channel_id,cursor=cursor)

# Print results
print(f"{len(conversation_history):d} messages found in {channel_id:s}")

bot_messages = []
for message in conversation_history:
    if message["user"]!=bot_userid:
        continue
    if "subtype" in message and message["subtype"] == "channel_join":
        continue
    message.pop("blocks")
    message.pop("bot_profile")
    bot_messages.append(message)

# Print results
print(f"{len(bot_messages):d} bot messages found in {channel_id:s}")

with open(save_to_file,"w") as f:
    json.dump(bot_messages,f,indent=4)

print(f"finished successfully, saved to {save_to_file:s}")
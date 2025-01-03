from flask import Flask, request, abort
from linebot.v3 import LineBotApi, WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.models import MemberJoinedEvent, TextSendMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
from dotenv import load_dotenv

app = Flask(__name__)

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info( ReplyMessageRequest( reply_token=event.reply_token, messages=[TextMessage(text=event.message.text)]))

# memberJoined event
@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    # Default name
    account_name = "Line Bot"
    group_name = "Toronto travel community"

    # Greeting template
    welcome_template = (
        "Hi {Nickname}, welcome to the Toronto DT Group! I’m {AccountName} (moon wink). Please click on the group notes to check out the latest meetup details (calendar). You can view photos of our past events in the album! (please!) (shiny) If you know friends living near downtown Toronto, feel free to invite them to join! (blue check mark) There’s no official group leader here, so feel free to organize activities and explore life in Canada together! (magnifying glass)"
    )

    # memberjoined
    for member in event.joined.members:
        if member.type == "user":
            # line_bot_api.get_profile()
            try:
                profile = line_bot_api.get_profile(member.user_id)
                nickname = profile.display_name  # nickname
            except Exception:
                nickname = "new member"  # if didn't catch

            # customized
            welcome_message = welcome_template.format(
                nickname=nickname, group_name=group_name, account_name=account_name
            )

            # welcome message
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=welcome_message)
            )

if __name__ == "__main__":
    app.run()


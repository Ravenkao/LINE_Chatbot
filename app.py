from flask import Flask, request, abort
from linebot.v3 import LineBotApi, WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.models import MemberJoinedEvent, TextSendMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
from dotenv import load_dotenv

app = Flask(__name__)

configuration = Configuration(access_token='ESypFeRu3VzDuLFeRS+iRN/yMy6Evno+x67XFpuJFxtA/N6z8giWfY85A1+FctwkjyMvE3j5RAXqQM+E6AduWW60NWbevwV5bvTz/ePa/hZt0G2Ry350NX0g3t3APSP+LuhXXVTVn3DeD6kvGXoddAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('588ade68aab86dac55e4523a6ae9c290')


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

# 處理 memberJoined 事件
@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    # 預設暱稱和帳號名稱，這可以根據實際需求修改
    account_name = "Line Bot"
    group_name = "多倫多 DT 團"

    # 歡迎訊息模版
    welcome_template = (
        "Hi {nickname}, 歡迎加入{group_name}！我是 {account_name} (moon wink)\n\n"
        "請點擊群組的記事本查詢最新的揪團訊息 (calendar)\n"
        "點擊相簿可以看到我們過去舉辦的活動！(please!)(shiny)\n"
        "如果你有認識的朋友居住在多倫多 DT 附近，歡迎邀請加入！(blue check mark)\n"
        "這裡沒有特別的團長，歡迎踴躍的發起活動，一起體驗加拿大生活！(magnifying glass)"
    )

    # 處理加入的成員
    for member in event.joined.members:
        if member.type == "user":
            # 注意：Line 平台不會直接提供用戶暱稱，你需要透過 `line_bot_api.get_profile()` 獲取
            try:
                profile = line_bot_api.get_profile(member.user_id)
                nickname = profile.display_name  # 用戶暱稱
            except Exception:
                nickname = "新成員"  # 若無法獲取，則使用預設名稱

            # 格式化歡迎訊息
            welcome_message = welcome_template.format(
                nickname=nickname, group_name=group_name, account_name=account_name
            )

            # 發送歡迎訊息
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=welcome_message)
            )

if __name__ == "__main__":
    app.run()

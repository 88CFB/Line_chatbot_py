import os
import MongoDB as mongo
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import pymongo

# 连接到MongoDB数据库
myClient = pymongo.MongoClient("mongodb://localhost:27017/")
dblist = myClient['lineBot']

app = Flask(__name__)

load_dotenv(dotenv_path='secret.env')
Line_bot_token = os.getenv('LINE_BOT_TOKEN')
channel_secret = os.getenv('CHANNEL_SECRET')  # 在.env文件中添加你的应用ID

configuration = Configuration(access_token=Line_bot_token)
handler = WebhookHandler(channel_secret)

api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)


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


def weather_create_user(collection_name, user_id):
    collection = dblist[collection_name]
    user = collection.find_one({"user_id": user_id})

    if not user:
        if collection_name == "sport":
            user_data = {
                "user_id": user_id,
                "time": None,
                "distance": None,
                "times": None,
            }
        elif collection_name == "health":
            user_data = {
                "user_id": user_id,
                "Maximal-Heart-Rate(MHR)": None,
                "Systolic-blood-pressure": None,
                "Diastolic-blood-pressure": None,
                "Height": None,
                "Weight": None
            }
        else: return None
        collection.insert_one(user_data)

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    reply_token = event.reply_token
    user_id = event.source.user_id  # 获取用户ID
    if user_message == "運動":
        weather_create_user("sport", user_id)
        sport(reply_token, user_id)
    elif user_message == "健康":
        weather_create_user("health", user_id)
        health(reply_token, user_id)


def sport(reply_token, user_id):
    # 在这里写运动相关的回复逻辑
    results = mongo.find_site("sport", user_id)
    response_message = ""
    for result in results:
        response_message += f"用户 {user_id} 的運動數據：\n"
        response_message += (f"運動時間: {result['time']}\n"
                             f"運動距離: {result['distance']}\n"
                             f"運動次數: {result['times']}次")
        # 根据需要添加其他字段
    if response_message:
        # 如果有找到相关数据，将结果发送给用户
        response_message = "以下是您的運動數據：\n" + response_message
    else:
        # 如果没有找到相关数据，给出提示信息
        response_message = "您還未輸入運動數據。"

    # 发送回复消息给用户
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=response_message)]
            )
        )


def health(reply_token, user_id):
    # 在这里写运动相关的回复逻辑
    results = mongo.find_site("health", user_id)
    response_message = ""
    for result in results:
        response_message += f"用户 {user_id} 的健康數據：\n"
        response_message += (f"最高心跳速率: {result['Maximal-Heart-Rate(MHR)']} Bpm\n"
                             f"收縮壓: {result['Systolic-blood-pressure']}mmHg\n"
                             f"舒張壓: {result['Diastolic-blood-pressure']}mmHg\n"
                             f"身高: {result['Height']}cm\n"
                             f"體重: {result['Weight']}kg\n")
        # 根据需要添加其他字段
    if response_message:
        # 如果有找到相关数据，将结果发送给用户
        response_message = "以下是您的健康數據：\n" + response_message
    else:
        # 如果没有找到相关数据，给出提示信息
        response_message = "您還未輸入健康數據。"

    # 发送回复消息给用户
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=response_message)]
            )
        )



if __name__ == "__main__":
    app.run()

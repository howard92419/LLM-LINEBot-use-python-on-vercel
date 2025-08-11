import os
import io
import requests
from api.llm import ChatGPT
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
web_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default="true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

# domain root
@app.route('/')
def home():
    return '<h1>Hello World</h1>'

# Listen for all Post Requests from /callback
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        web_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def start_loading_animation(chat_id, loading_seconds):
    url = "https://api.line.me/v2/bot/chat/loading/start"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}"
    }
    data = {
        "chatId": chat_id,
        "loadingSeconds": loading_seconds
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code

@web_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """LINE MessageAPI message processing"""
    if event.source.user_id == 'Udeadbeefdeadbeefdeadbeefdeadbeef':
        return 'OK'
    
    global working_status

    if event.message.type != "text":
        return

    if event.message.text[:3] == "啟動":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="啟動AI"))
        return

    if event.message.text[:5] == "關閉AI":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='AI下班去，喚醒請輸入"啟動"'))
        return

    if working_status:
        start_loading_animation(event.source.user_id, 5)
        chatgpt.add_msg(f"HUMAN:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        
        questions = ["了解更多", "出2個練習題","相關文獻", "相關觀念"]
        # 將追問問題設為 Quick Replies
        quick_reply_buttons = [
            QuickReplyButton(action=MessageAction(label=question, text=question))
            for question in questions
        ]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=reply_msg, 
                quick_reply=QuickReply(items=quick_reply_buttons)
            )
        )

@web_handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    # 1) 向 LINE 取圖
    resp = line_bot_api.get_message_content(event.message.id)  # requests.Response
    img_bytes = b"".join(chunk for chunk in resp.iter_content())

    # 2) 轉 base64 -> data URL（模型一定讀得到）
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{b64}"

    # 3) 呼叫 OpenAI 的 chat.completions（多模態）
    prompt = "請閱讀這張圖片的重點內容，條列出主要步驟/資訊。"
    oai = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    )

    # 4) 正確取回傳內容
    reply_msg = oai.choices[0].message.content

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"助教：{reply_msg}")
    )

if __name__ == "__main__":
    app.run()

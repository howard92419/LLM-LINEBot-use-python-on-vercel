import os
import io
import requests
from api.llm import ChatGPT
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction
import logging

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
    print(body)
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
    try:
        print(f"[DEBUG] 收到訊息類型：{event.message.type}")

        if event.message.type == "image":
            message_id = event.message.id
            print(f"[DEBUG] 收到圖片 ID：{message_id}")

            # 回應文字確認收到圖片
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"📷 我收到你的圖片囉！（ID: {message_id}）")
            )
            return

        if event.message.type != "text":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"我目前只懂文字訊息，你傳的是 {event.message.type}。")
            )
            return

        # 以下處理純文字訊息
        if event.message.text[:3] == "啟動":
            global working_status
            working_status = True
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="✅ AI 已啟動！")
            )
            return

        if event.message.text[:5] == "關閉AI":
            working_status = False
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="🛑 AI 已關閉，輸入「啟動」可重新開始")
            )
            return

        if working_status:
            question = event.message.text
            chatgpt.add_msg(f"HUMAN:{question}?\n")
            response = chatgpt.get_response()

            if not response:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="⚠️ 抱歉，我沒收到有效的回應，請再試一次")
                )
                return

            reply_msg = response.replace("AI:", "", 1)
            chatgpt.add_msg(f"AI:{reply_msg}\n")

            questions = ["了解更多", "出2個練習題", "相關文獻", "相關觀念"]
            quick_reply_buttons = [
                QuickReplyButton(action=MessageAction(label=q, text=q))
                for q in questions
            ]

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=reply_msg,
                    quick_reply=QuickReply(items=quick_reply_buttons)
                )
            )
            return

        # 如果 AI 沒啟動，就告訴使用者
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="💤 AI 尚未啟動，請輸入「啟動」來開始使用。")
        )

    except Exception as e:
        import logging
        logging.exception("⚠️ webhook 處理錯誤：")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="❗ 發生錯誤，請稍後再試一次")
        )

@web_handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    try:
        print("[DEBUG] 收到圖片訊息")

        # 1. 下載圖片
        image_content = line_bot_api.get_message_content(event.message.id)
        print("[DEBUG] 圖片內容已下載")

        # 2. 儲存圖片
        path = chatgpt.get_user_image(image_content)
        print(f"[DEBUG] 圖片已儲存到：{path}")

        # 3. 上傳圖檔，取得公開連結
        link = chatgpt.upload_img_link(path)
        print(f"[DEBUG] 圖片上傳完成，網址為：{link}")

        # 4. 呼叫 OpenAI 分析圖片
        response = chatgpt.process_image_link(link)
        print(f"[DEBUG] OpenAI 分析完成：{response}")

        # 5. 解析並回覆
        reply_msg = response['choices'][0]['text']
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"助教：{reply_msg}")
        )

    except Exception as e:
        import traceback
        print("[ERROR] 圖片處理錯誤：", e)
        traceback.print_exc()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="❗ 圖片處理時發生錯誤，請稍後再試")
        )

if __name__ == "__main__":
    app.run()

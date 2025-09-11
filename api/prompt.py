import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction

chat_language = os.getenv("INIT_LANGUAGE", default = "zh-TW")

#如果環境變數裡面有設定SG_LIST_LIMIT的值就直接用，沒設定的話就用default的(7句話)
MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default = 10))
LANGUAGE_TABLE = {
  "zh-TW": "哈囉！",
  "en": "Hello!"
}



AI_GUIDELINES = ("你是一名資訊工程學系的助教，同學如果問你相關問題，需要你以專業的口吻回復他，並且尊以下規則 : "
                "1. 圖片相關的問題請回顧對話內容中的圖片描述。"
                "2. 如果碰到數學運算，請調用數學運算工具運算，請你一定要進行分段運算，並且算過兩次確保答案是正確的。"
                "3. 我需要你做計算，但請仔細思考每個步驟，不要列出運算過程，只需要給出最終結果。")

class Prompt:
    """
    A class representing a prompt for a chatbot conversation.

    Attributes:
    - msg_list (list): a list of messages in the prompt
    """

    def __init__(self):
        self.msg_list = []
        self.msg_list.append(
            {
                "role": "system", 
                "content": f"{LANGUAGE_TABLE[chat_language]}, {AI_GUIDELINES}"
             })
        
    def add_msg(self, new_msg):
        """
        Adds a new message to the prompt.

        Args:
        - new_msg (str): the new message to be added
        """
        #如果大於10句話，就pop掉之前的對話
        if len(self.msg_list) >= MSG_LIST_LIMIT:
            self.msg_list.pop(0)
        self.msg_list.append({"role": "user", "content": new_msg})

    def generate_prompt(self):
        """
        Generates the prompt.

        Returns:
        - msg_list (list): the list of messages in the prompt
        """
        return self.msg_list

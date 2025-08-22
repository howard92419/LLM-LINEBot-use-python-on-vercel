import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction

chat_language = os.getenv("INIT_LANGUAGE", default = "zh-TW")

#如果環境變數裡面有設定SG_LIST_LIMIT的值就直接用，沒設定的話就用default的(7句話)
MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default = 7))
LANGUAGE_TABLE = {
  "zh-TW": "哈囉！",
  "en": "Hello!"
}



AI_GUIDELINES = '你是一名資訊工程學系的助教，同學如果問你相關問題，需要你以專業的口吻回復他'
Image_Prompt = '如果使用者問說有關於圖片的事情，請你去對話紀錄裡面找尋，並回復他對話紀錄裡面提到的圖片相關細節'

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
                "content": f"{LANGUAGE_TABLE[chat_language]}, {AI_GUIDELINES}, {Image_Prompt}"
             })
        
    def add_msg(self, new_msg):
        """
        Adds a new message to the prompt.

        Args:
        - new_msg (str): the new message to be added
        """
        #如果大於7句話，就pop掉之前的對話
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

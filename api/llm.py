from api.prompt import Prompt
import os
from openai import OpenAI
import pyimgur
import base64

client = OpenAI()

client.api_key = os.getenv("OPENAI_API_KEY")

class ChatGPT:
    """
    A class for generating responses using OpenAI's GPT model.

    Attributes:
    - prompt: an instance of the Prompt class for generating prompts
    - model: a string representing the name of the OpenAI model to use
    - temperature: a float representing the "creativity" of the responses generated
    - max_tokens: an integer representing the maximum number of tokens to generate in a response
    """

    def __init__(self, gpt_model = "gpt-4o"):
        self.prompt = Prompt()
        self.model = gpt_model
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default=0))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default=600))
        self.image_memory = []

    def change_model(self, new_model):
        self.model = new_model
    
    def get_response(self):
        """
        Generates a response using OpenAI's GPT model.

        Returns:
        - A string representing the generated response.
        """

        response = client.chat.completions.create(
            model=self.model,
            #generate_prompt會強迫GPT去看之前7則的對話內容
            messages=self.prompt.generate_prompt(),
        )
        #choices是GPT的回應內容，choices是一個list，通常GPT會有好幾種不同的回應，我們只選取第一種回應
        return response.choices[0].message.content

    def add_msg(self, text):
        """
        Adds a message to the prompt for generating a response.

        Parameters:
        - text: a string representing the message to add to the prompt.
        """
        self.prompt.add_msg(text)

    def get_user_image(self, image_content):
        #/tmp/是大部分雲端平台和伺服器允許寫入的唯一目錄，是臨時儲存空間，在這邊我用來暫存等等要處理的圖片
        temp_path = "/tmp/temp.png"


        with open(temp_path, 'wb') as f:
            #將image切成很多chunk存入temp_path，因為如果圖片檔很大一次存入可overflow
            #image_content 是來自 LINE 的圖片資料
            for chunk in image_content.iter_content():
                f.write(chunk)
        return temp_path
    
    def get_user_file(self, file_content):
        pdf_path = "/tmp/temp.pdf"

        with open(pdf_path, "wb") as f:
            for chunk in file_content.iter_content():
                f.write(chunk)
        return pdf_path

        
    '''GPT支援URL，但有限制條件，例如...必須是http  or 可直接載入的圖片，不然就是要把圖片使用base 64 encode
    此process_image_file() function作用為將圖片轉換為base 64 編碼'''

    def process_image_file(self, img_path):#轉成base 64的function
        with open(img_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        base64_data_url = f"data:image/png;base64,{base64_image}"
        self.add_msg("HUMAN: 我剛剛上傳了一張圖片，可以記住嗎？")

        response = client.chat.completions.create(
            model=gpt_model,
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "請對所附圖片做全面、精確的分析：\n"
                                "1. **多次檢視**：至少讀取兩遍，確保不遺漏任何細節和數字。\n"
                                "2. **元素列表**：列出所有視覺元素（表格、欄位標題、欄目、文字、圖形等）。\n"
                                "3. **數字保真**：記住並復述圖片中的所有數字，不得遺漏或錯誤。\n"
                                "4. **後續依據**：後續任何有關此圖片的提問，都要基於此分析結果回答。\n"
                                "5. **數學計算**：凡涉及加減乘除，一律呼叫數學工具計算；其中「加法」請拆分分段相加，不要展示中間計算過程。\n\n"
                                "嚴格要求：\n"
                                "- 如果沒有特別提說要進行數學運算，不能先自行進行運算"
                                "- 不得以任何理由聲稱「無法記住或存儲詳細資訊」。\n"
                                "- 必須完整、準確地保留並運用圖片內所有文字與數字。"
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_data_url
                            }
                        }
                    ]
                }
        ]
        )
        reply_text = response.choices[0].message.content
        self.add_msg(f"AI: {reply_text}")

        self.image_memory.append({
            "path": img_path,
            "description": reply_text
        })
        return reply_text
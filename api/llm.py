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

    def __init__(self):
        self.prompt = Prompt()
        self.model = os.getenv("OPENAI_MODEL", default="gpt-4o-mini")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default=0))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default=600))

    def get_response(self):
        """
        Generates a response using OpenAI's GPT model.

        Returns:
        - A string representing the generated response.
        """
        response = client.chat.completions.create(
            model=self.model,
            messages=self.prompt.generate_prompt(),
        )
        return response.choices[0].message.content

    def add_msg(self, text):
        """
        Adds a message to the prompt for generating a response.

        Parameters:
        - text: a string representing the message to add to the prompt.
        """
        self.prompt.add_msg(text)

    def get_user_image(self, image_content):
        temp_path = "/tmp/temp.png"
        with open(temp_path, 'wb') as f:
            for chunk in image_content.iter_content():
                f.write(chunk)
        return temp_path 
        
    '''GPT支援URL，但有限制條件，例如...必須是http  or 可直接載入的圖片，不然就是要把圖片使用base 64 encode
    此process_image_file() function作用為將圖片轉換為base 64 編碼'''

    def process_image_file(self, img_path):
        with open(img_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        base64_data_url = f"data:image/png;base64,{base64_image}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "請幫我分析這張圖片"},
                        {"type": "image_url", "image_url": {"url": base64_data_url}}
                    ]
                }
            ]
        )
        return response.choices[0].message.content

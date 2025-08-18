from api.prompt import Prompt
import os
from openai import OpenAI
import pyimgur
import base64
import cloudinary
import cloudinary.uploader

cloudinary.config( 
  cloud_name = "dignwsyyd", 
  api_key = "947292761547843", 
  api_secret = "pORjKjloUwbcIw5lKu1Lvzge_bc"
)

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

    def process_image_link(self, image_url):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "請幫我分析這張圖片"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]
        )
        return response.choices[0].message.content

    def get_user_image(self, image_content):
        temp_path = "/tmp/temp.png"
        with open(temp_path, 'wb') as f:
            for chunk in image_content.iter_content():
                f.write(chunk)
        return temp_path


    def upload_img_link(self, img_path):
        try:
            result = cloudinary.uploader.upload(img_path)
            return result['secure_url']
        except Exception as e:
            print("[ERROR] Cloudinary upload failed:", e)
            return None
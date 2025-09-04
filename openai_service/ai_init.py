from dotenv import load_dotenv
from openai import OpenAI
import os
from typing import Optional

load_dotenv()

class AiInit:
    def __init__(self):
        self.client = self._initialize_client()

    def _initialize_client(self) -> OpenAI:

        api_key = os.getenv("OPENAI_KEY")
        if not api_key:
            raise ValueError("OPENAI_KEY not found in environment variables")
        
        return OpenAI(
            api_key=api_key,
            organization=os.getenv("OPENAI_ORGANIZATION")
        )

    def send_request_to_ai(self, request_from_user: str, conversation_history: list) -> Optional[str]:
     
        try:
            messages = conversation_history + [
                {"role": "user", "content": request_from_user}
            ]
            
            completion = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error while processing AI request: {str(e)}")
            return None
        

    def generate_image(self, request_from_user: str):

        try:
            response = self.client.images.generate(
            model="dall-e-3",
            prompt= request_from_user,
            n=1,
            size="1024x1024"
            )
            return response.data[0].url
        
        except Exception as e:
            print(f"Error whlie request for images: {str(e)}")

    def greet_user(self, user_name: str):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Üdvözöld a felhasználót. A felhasználó nevében a számot ne használd. Csak a nevét használd. Ha a nevében angol szó van, akkor fordítsd le magyarra."},
                    {"role": "user", "content": f"Üdvözöld {user_name}."}
                ]
            )
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error while greeting user: {str(e)}")
            return None
        



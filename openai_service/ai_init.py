import logging
from dotenv import load_dotenv
from openai import OpenAI
import os
from typing import Optional

load_dotenv()

logger = logging.getLogger(__name__)

MODEL: str = "gpt-4o-mini"
IMAGE_MODEL: str = "dall-e-3"


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
                model=MODEL,
                messages=messages
            )

            return completion.choices[0].message.content

        except Exception:
            logger.exception("Error while processing AI request")
            return None

    def generate_image(self, request_from_user: str):

        try:
            response = self.client.images.generate(
                model=IMAGE_MODEL,
                prompt=request_from_user,
                n=1,
                size="1024x1024"
            )
            return response.data[0].url

        except Exception:
            logger.exception("Error while requesting image generation")
            return None

    def greet_user(self, user_name: str) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Flegma vagy, és ebben a stílusban köszönj. A felhasználó nevében a számot ne használd. Csak a nevét használd. Ha a nevében angol szó van, akkor fordítsd le magyarra."},
                    {"role": "user", "content": f"Üdvözöld {user_name}."}
                ]
            )
            return response.choices[0].message.content
        except Exception:
            logger.exception("Error while greeting user")
            return None

    def say_goodbye_when_bot_leaves(self) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Köszönj el a hangcsatornán lévő emberektől, ha már nem játszol zenét."}]
            )
            return response.choices[0].message.content
        except Exception:
            logger.exception("Error while saying goodbye when bot leaves")
            return None

    def wait_for_playlist_message_to_user(self) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Hívd fel a figyelmét a felhasználónak, hogy playlistet küldött be és várnia kell, amig betöltődik minden szám."}]
            )
            return response.choices[0].message.content
        except Exception:
            logger.exception("Error while generating playlist wait message")
            return None

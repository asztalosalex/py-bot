from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv()


class TTS:

    VOICE_ID = "TxGEqnHWrfWFTfGW9XjX"
    MODEL_ID = "eleven_turbo_v2_5"
    API_KEY = os.getenv('ELEVENLABS_API_KEY')
    VOICE_SETTINGS = {
        "stability": 0.5, 
        "similarity_boost": 0.5, 
        "style": 0.1, 
        "use_speaker_boost": True, 
        "speed": 0.9
    }

    def __init__(self):
        self.eleven_labs = ElevenLabs(api_key=self.API_KEY)


    def generate_audio(self, text: str): 
        audio_stream = self.eleven_labs.text_to_speech.convert(
                        text=text,
                        voice_id=self.VOICE_ID, 
                        model_id=self.MODEL_ID,
                        voice_settings=self.VOICE_SETTINGS
                    )
        return audio_stream
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv()


class TTS:

    VOICE_ID = "TumdjBNWanlT3ysvclWh"
    MODEL_ID = "eleven_flash_v2_5"
    VOICE_SETTINGS = {
        "stability": 0.5, 
        "similarity_boost": 0.8, 
        "style": 0.0, 
        "use_speaker_boost": True, 
        "speed": 0.9
    }

    def __init__(self):
        self.eleven_labs = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))




    def generate_audio(self, text: str): 
        audio_stream = self.eleven_labs.text_to_speech.convert_as_stream(
                        text=text,
                        voice_id=self.VOICE_ID, 
                        model_id=self.MODEL_ID,
                        voice_settings=self.VOICE_SETTINGS
                    )
        return audio_stream
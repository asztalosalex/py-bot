from unittest.mock import MagicMock, patch

from tts.tts import TTS


def test_generate_audio_calls_elevenlabs_with_expected_params():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = iter([b"chunk1", b"chunk2"])

    with patch("tts.tts.ElevenLabs", return_value=mock_client):
        tts = TTS()
        result = list(tts.generate_audio("hello"))

    assert result == [b"chunk1", b"chunk2"]
    mock_client.text_to_speech.convert.assert_called_once_with(
        text="hello",
        voice_id=TTS.VOICE_ID,
        model_id=TTS.MODEL_ID,
        voice_settings=TTS.VOICE_SETTINGS,
    )

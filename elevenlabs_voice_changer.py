"""
ElevenLabs Voice Changer Node for ComfyUI
Uses the ElevenLabs Speech-to-Speech API to transform voices in audio files.
"""

import os
import tempfile
from io import BytesIO

class ElevenLabsVoiceChanger:
    """
    ComfyUI node that uses ElevenLabs Speech-to-Speech API to change voices in audio.
    """

    MODELS = [
        "eleven_multilingual_sts_v2",
        "eleven_english_sts_v2",
    ]

    OUTPUT_FORMATS = [
        "mp3_44100_128",
        "mp3_44100_192",
        "mp3_22050_32",
        "pcm_16000",
        "pcm_22050",
        "pcm_24000",
        "pcm_44100",
        "ulaw_8000",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "voice_id": ("STRING", {
                    "default": "JBFqnCBsd6RMkjVDRZzb",
                    "multiline": False,
                }),
            },
            "optional": {
                "model_id": (cls.MODELS, {
                    "default": "eleven_multilingual_sts_v2",
                }),
                "output_format": (cls.OUTPUT_FORMATS, {
                    "default": "mp3_44100_128",
                }),
                "remove_background_noise": ("BOOLEAN", {
                    "default": False,
                }),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "convert_voice"
    CATEGORY = "audio/ElevenLabs"

    def convert_voice(self, audio, api_key, voice_id, model_id="eleven_multilingual_sts_v2",
                      output_format="mp3_44100_128", remove_background_noise=False):
        """
        Convert the voice in the input audio using ElevenLabs Speech-to-Speech API.

        Args:
            audio: Input audio (ComfyUI AUDIO type - dict with 'waveform' and 'sample_rate')
            api_key: ElevenLabs API key
            voice_id: Target voice ID from ElevenLabs
            model_id: Model to use for conversion
            output_format: Output audio format
            remove_background_noise: Whether to remove background noise

        Returns:
            tuple: (audio_output,) - The converted audio
        """
        try:
            from elevenlabs.client import ElevenLabs
        except ImportError:
            raise ImportError(
                "Please install the elevenlabs package: pip install elevenlabs"
            )

        try:
            import torchaudio
            import torch
        except ImportError:
            raise ImportError(
                "Please install torchaudio: pip install torchaudio"
            )

        if not api_key:
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key is required. Provide it as input or set ELEVENLABS_API_KEY environment variable."
                )

        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=api_key)

        # Convert ComfyUI audio format to bytes
        # ComfyUI AUDIO type is a dict with 'waveform' (tensor) and 'sample_rate' (int)
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]

        # Ensure waveform is 2D (channels, samples)
        if waveform.dim() == 3:
            # Shape is (batch, channels, samples) - take first batch
            waveform = waveform[0]

        # Save to temporary file for API
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Save waveform to MP3
            torchaudio.save(tmp_path, waveform, sample_rate, format="mp3")

            # Read file and send to API
            with open(tmp_path, "rb") as f:
                audio_data = BytesIO(f.read())

            # Call ElevenLabs Speech-to-Speech API
            audio_stream = client.speech_to_speech.convert(
                voice_id=voice_id,
                audio=audio_data,
                model_id=model_id,
                output_format=output_format,
                remove_background_noise=remove_background_noise,
            )

            # Collect the audio stream into bytes
            audio_bytes = b"".join(audio_stream)

            # Save response to temporary file for loading
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as out_file:
                out_path = out_file.name
                out_file.write(audio_bytes)

            try:
                # Load the converted audio
                converted_waveform, converted_sample_rate = torchaudio.load(out_path)

                # Add batch dimension for ComfyUI format
                if converted_waveform.dim() == 2:
                    converted_waveform = converted_waveform.unsqueeze(0)

                # Return in ComfyUI AUDIO format
                output_audio = {
                    "waveform": converted_waveform,
                    "sample_rate": converted_sample_rate,
                }

                return (output_audio,)

            finally:
                # Clean up output temp file
                if os.path.exists(out_path):
                    os.unlink(out_path)

        finally:
            # Clean up input temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "ElevenLabsVoiceChanger": ElevenLabsVoiceChanger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ElevenLabsVoiceChanger": "ElevenLabs Voice Changer",
}

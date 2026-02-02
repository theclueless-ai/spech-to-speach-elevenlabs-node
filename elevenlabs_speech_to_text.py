"""
ElevenLabs Speech-to-Text Node for ComfyUI
Uses the ElevenLabs Speech-to-Text API (Scribe) to transcribe audio to text.
"""

import os
import struct
from io import BytesIO


class ElevenLabsSpeechToText:
    """
    ComfyUI node that uses ElevenLabs Speech-to-Text API to transcribe audio.
    """

    MODELS = [
        "scribe_v1",
        "scribe_v1_experimental",
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
            },
            "optional": {
                "model_id": (cls.MODELS, {
                    "default": "scribe_v1",
                }),
                "language_code": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "tag_audio_events": ("BOOLEAN", {
                    "default": False,
                }),
                "num_speakers": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 32,
                }),
                "timestamps_granularity": (["none", "word", "character"], {
                    "default": "none",
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "transcribe"
    CATEGORY = "audio/ElevenLabs"

    def transcribe(self, audio, api_key, model_id="scribe_v1", language_code="",
                   tag_audio_events=False, num_speakers=0, timestamps_granularity="none"):
        """
        Transcribe audio to text using ElevenLabs Speech-to-Text API.

        Args:
            audio: Input audio (ComfyUI AUDIO type - dict with 'waveform' and 'sample_rate')
            api_key: ElevenLabs API key
            model_id: Model to use for transcription
            language_code: Language code (e.g., 'en', 'es', 'fr') - empty for auto-detect
            tag_audio_events: Whether to tag non-speech audio events (laughter, applause, etc.)
            num_speakers: Expected number of speakers (0 for auto-detect, max 32)
            timestamps_granularity: Level of timestamp detail ('none', 'word', 'character')

        Returns:
            tuple: (transcribed_text,)
        """
        try:
            from elevenlabs.client import ElevenLabs
        except ImportError:
            raise ImportError(
                "Please install the elevenlabs package: pip install elevenlabs"
            )

        try:
            import numpy as np
        except ImportError:
            raise ImportError(
                "Please install numpy"
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
        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]

        # Ensure waveform is 2D (channels, samples)
        if waveform.dim() == 3:
            waveform = waveform[0]

        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        # Convert to numpy array for WAV creation
        waveform_np = waveform.cpu().numpy().T

        # Convert float32 [-1, 1] to int16 for WAV
        waveform_int16 = (np.clip(waveform_np, -1, 1) * 32767).astype(np.int16)

        # Create WAV file bytes
        audio_bytes = self._create_wav_bytes(waveform_int16, sample_rate)

        # Build API call parameters
        api_params = {
            "file": audio_bytes,
            "model_id": model_id,
        }

        # Add optional parameters
        if language_code:
            api_params["language_code"] = language_code

        if tag_audio_events:
            api_params["tag_audio_events"] = tag_audio_events

        if num_speakers > 0:
            api_params["num_speakers"] = num_speakers

        if timestamps_granularity != "none":
            api_params["timestamps_granularity"] = timestamps_granularity

        # Call ElevenLabs Speech-to-Text API
        result = client.speech_to_text.convert(**api_params)

        # Extract the transcribed text
        transcribed_text = result.text if hasattr(result, 'text') else str(result)

        return (transcribed_text,)

    def _create_wav_bytes(self, audio_data, sample_rate):
        """Create WAV file bytes from audio data."""
        if audio_data.ndim == 1:
            audio_data = audio_data.reshape(-1, 1)

        num_samples, num_channels = audio_data.shape
        bytes_per_sample = 2

        wav_header = BytesIO()
        wav_header.write(b'RIFF')
        data_size = num_samples * num_channels * bytes_per_sample
        file_size = 36 + data_size
        wav_header.write(struct.pack('<I', file_size))
        wav_header.write(b'WAVE')
        wav_header.write(b'fmt ')
        wav_header.write(struct.pack('<I', 16))
        wav_header.write(struct.pack('<H', 1))
        wav_header.write(struct.pack('<H', num_channels))
        wav_header.write(struct.pack('<I', sample_rate))
        byte_rate = sample_rate * num_channels * bytes_per_sample
        wav_header.write(struct.pack('<I', byte_rate))
        block_align = num_channels * bytes_per_sample
        wav_header.write(struct.pack('<H', block_align))
        wav_header.write(struct.pack('<H', bytes_per_sample * 8))
        wav_header.write(b'data')
        wav_header.write(struct.pack('<I', data_size))

        return wav_header.getvalue() + audio_data.tobytes()


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "ElevenLabsSpeechToText": ElevenLabsSpeechToText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ElevenLabsSpeechToText": "ElevenLabs Speech to Text",
}

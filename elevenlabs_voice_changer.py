"""
ElevenLabs Voice Changer Node for ComfyUI
Uses the ElevenLabs Speech-to-Speech API to transform voices in audio files.
"""

import os
import tempfile
import struct
from io import BytesIO

class ElevenLabsVoiceChanger:
    """
    ComfyUI node that uses ElevenLabs Speech-to-Speech API to change voices in audio.
    """

    MODELS = [
        "eleven_multilingual_sts_v2",
        "eleven_english_sts_v2",
    ]

    # MP3 formats (available for all tiers) + PCM formats (Pro tier only)
    OUTPUT_FORMATS = [
        "mp3_44100_128",
        "mp3_44100_192",
        "mp3_22050_32",
        "pcm_44100",
        "pcm_24000",
        "pcm_22050",
        "pcm_16000",
    ]

    # Map format to sample rate
    FORMAT_SAMPLE_RATES = {
        "mp3_44100_128": 44100,
        "mp3_44100_192": 44100,
        "mp3_22050_32": 22050,
        "pcm_44100": 44100,
        "pcm_24000": 24000,
        "pcm_22050": 22050,
        "pcm_16000": 16000,
    }

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
        """
        try:
            from elevenlabs.client import ElevenLabs
        except ImportError:
            raise ImportError(
                "Please install the elevenlabs package: pip install elevenlabs"
            )

        try:
            import torch
            import numpy as np
        except ImportError:
            raise ImportError(
                "Please install torch and numpy"
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

        # Create WAV file manually
        audio_bytes = self._create_wav_bytes(waveform_int16, sample_rate)
        audio_data = BytesIO(audio_bytes)

        # Call ElevenLabs Speech-to-Speech API
        audio_stream = client.speech_to_speech.convert(
            voice_id=voice_id,
            audio=audio_data,
            model_id=model_id,
            output_format=output_format,
            remove_background_noise=remove_background_noise,
        )

        # Collect the audio stream into bytes
        response_bytes = b"".join(audio_stream)

        # Get the sample rate for the output format
        output_sample_rate = self.FORMAT_SAMPLE_RATES.get(output_format, 44100)

        # Convert response to tensor based on format
        if output_format.startswith("mp3"):
            converted_waveform, actual_sample_rate = self._mp3_bytes_to_tensor(response_bytes)
            output_sample_rate = actual_sample_rate
        else:
            converted_waveform = self._pcm_bytes_to_tensor(response_bytes, output_sample_rate)

        # Return in ComfyUI AUDIO format
        output_audio = {
            "waveform": converted_waveform,
            "sample_rate": output_sample_rate,
        }

        return (output_audio,)

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

    def _pcm_bytes_to_tensor(self, pcm_bytes, sample_rate):
        """Convert raw PCM bytes to a PyTorch tensor."""
        import torch
        import numpy as np

        audio_array = np.frombuffer(pcm_bytes, dtype=np.int16)
        audio_float = audio_array.astype(np.float32) / 32767.0
        waveform = torch.from_numpy(audio_float).unsqueeze(0).unsqueeze(0)

        return waveform

    def _mp3_bytes_to_tensor(self, mp3_bytes):
        """Convert MP3 bytes to a PyTorch tensor using miniaudio (no ffmpeg needed)."""
        import torch
        import numpy as np

        try:
            import miniaudio
        except ImportError:
            raise ImportError(
                "miniaudio is required for MP3 decoding. Install it with: pip install miniaudio"
            )

        # Decode MP3 bytes to raw audio
        decoded = miniaudio.decode(mp3_bytes, output_format=miniaudio.SampleFormat.SIGNED16)

        # Get audio properties
        sample_rate = decoded.sample_rate
        num_channels = decoded.nchannels

        # Convert to numpy array
        audio_array = np.array(decoded.samples, dtype=np.int16)

        # If stereo, convert to mono by averaging channels
        if num_channels > 1:
            audio_array = audio_array.reshape(-1, num_channels)
            audio_array = audio_array.mean(axis=1).astype(np.int16)

        # Normalize to float32 [-1, 1]
        audio_float = audio_array.astype(np.float32) / 32767.0

        # Convert to tensor: (1, 1, samples) for (batch, channels, samples)
        waveform = torch.from_numpy(audio_float).unsqueeze(0).unsqueeze(0)

        return waveform, sample_rate


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "ElevenLabsVoiceChanger": ElevenLabsVoiceChanger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ElevenLabsVoiceChanger": "ElevenLabs Voice Changer",
}

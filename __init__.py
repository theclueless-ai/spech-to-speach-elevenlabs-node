"""
ComfyUI Custom Nodes: ElevenLabs Audio Tools
- Voice Changer: Uses ElevenLabs Speech-to-Speech API to transform voices
- Speech to Text: Uses ElevenLabs Scribe API to transcribe audio
"""

from .elevenlabs_voice_changer import (
    NODE_CLASS_MAPPINGS as VOICE_CHANGER_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as VOICE_CHANGER_DISPLAY_MAPPINGS,
)
from .elevenlabs_speech_to_text import (
    NODE_CLASS_MAPPINGS as STT_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as STT_DISPLAY_MAPPINGS,
)

# Merge all node mappings
NODE_CLASS_MAPPINGS = {
    **VOICE_CHANGER_MAPPINGS,
    **STT_MAPPINGS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **VOICE_CHANGER_DISPLAY_MAPPINGS,
    **STT_DISPLAY_MAPPINGS,
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

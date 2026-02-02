"""
ComfyUI Custom Node: ElevenLabs Voice Changer
Uses ElevenLabs Speech-to-Speech API to transform voices in audio files.
"""

from .elevenlabs_voice_changer import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# ElevenLabs Audio Tools for ComfyUI

Custom ComfyUI nodes that use ElevenLabs APIs for audio processing.

## Nodes Included

1. **ElevenLabs Voice Changer** - Transform voices using Speech-to-Speech API
2. **ElevenLabs Speech to Text** - Transcribe audio using Scribe API

## Installation

1. Clone this repository into your ComfyUI custom_nodes folder:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-username/spech-to-speach-elevenlabs-node.git
```

2. Install dependencies:
```bash
cd spech-to-speach-elevenlabs-node
pip install -r requirements.txt
```

3. Restart ComfyUI

---

## Node: ElevenLabs Voice Changer

Transforms the voice in an audio file using ElevenLabs' Speech-to-Speech API.

### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `audio` | AUDIO | Yes | Input audio in ComfyUI AUDIO format |
| `api_key` | STRING | Yes | Your ElevenLabs API key |
| `voice_id` | STRING | Yes | Target voice ID from ElevenLabs |
| `model_id` | COMBO | No | Model to use (default: `eleven_multilingual_sts_v2`) |
| `output_format` | COMBO | No | Output audio format (default: `mp3_44100_128`) |
| `remove_background_noise` | BOOLEAN | No | Remove background noise (default: False) |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `audio` | AUDIO | Converted audio with the new voice |

### Available Models

- `eleven_multilingual_sts_v2` - Multilingual speech-to-speech model (recommended)
- `eleven_english_sts_v2` - English-only speech-to-speech model

### Available Output Formats

**MP3 (all tiers):**
- `mp3_44100_128` - MP3 at 44.1kHz, 128kbps (recommended)
- `mp3_44100_192` - MP3 at 44.1kHz, 192kbps
- `mp3_22050_32` - MP3 at 22.05kHz, 32kbps

**PCM (Pro tier only):**
- `pcm_44100` - PCM at 44.1kHz
- `pcm_24000` - PCM at 24kHz
- `pcm_22050` - PCM at 22.05kHz
- `pcm_16000` - PCM at 16kHz

---

## Node: ElevenLabs Speech to Text

Transcribes audio to text using ElevenLabs' Scribe API.

### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `audio` | AUDIO | Yes | Input audio in ComfyUI AUDIO format |
| `api_key` | STRING | Yes | Your ElevenLabs API key |
| `model_id` | COMBO | No | Model to use (default: `scribe_v1`) |
| `language_code` | STRING | No | Language code (e.g., 'en', 'es') - empty for auto-detect |
| `tag_audio_events` | BOOLEAN | No | Tag non-speech events like laughter (default: False) |
| `num_speakers` | INT | No | Expected number of speakers, 0 for auto (max: 32) |
| `timestamps_granularity` | COMBO | No | Timestamp detail level (default: `none`) |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `text` | STRING | Transcribed text |

### Available Models

- `scribe_v1` - Standard transcription model (recommended)
- `scribe_v1_experimental` - Experimental model with newer features

### Supported Languages

The API supports 90+ languages with automatic language detection. You can also specify a language code to improve accuracy:
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese
- And many more...

---

## Getting Your ElevenLabs API Key

1. Go to [ElevenLabs](https://elevenlabs.io)
2. Create an account or sign in
3. Navigate to your profile settings
4. Copy your API key

## Getting Voice IDs

You can find voice IDs in the ElevenLabs Voice Library or create your own voices.

Default voice ID: `JBFqnCBsd6RMkjVDRZzb` (George)

## Environment Variables

You can set your API key as an environment variable instead of entering it in the nodes:

```bash
export ELEVENLABS_API_KEY="your-api-key-here"
```

## Compatibility

These nodes are designed to work across all platforms:
- ComfyDeploy
- RunPod
- Local ComfyUI installations

They use minimal dependencies and don't require ffmpeg or torchaudio for audio I/O.

## License

MIT License

## Credits

- [ElevenLabs](https://elevenlabs.io) for the Speech-to-Speech and Speech-to-Text APIs
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) for the node framework

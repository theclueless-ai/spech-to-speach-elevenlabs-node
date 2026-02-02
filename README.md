# ElevenLabs Voice Changer Node for ComfyUI

A custom ComfyUI node that uses the ElevenLabs Speech-to-Speech API to transform voices in audio files.

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

## Usage

### Node: ElevenLabs Voice Changer

This node takes an audio input and converts the voice using ElevenLabs' Speech-to-Speech API.

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `audio` | AUDIO | Yes | Input audio in ComfyUI AUDIO format |
| `api_key` | STRING | Yes | Your ElevenLabs API key (or set `ELEVENLABS_API_KEY` env var) |
| `voice_id` | STRING | Yes | Target voice ID from ElevenLabs |
| `model_id` | COMBO | No | Model to use (default: `eleven_multilingual_sts_v2`) |
| `output_format` | COMBO | No | Output audio format (default: `mp3_44100_128`) |
| `remove_background_noise` | BOOLEAN | No | Remove background noise from input (default: False) |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `audio` | AUDIO | Converted audio with the new voice |

### Available Models

- `eleven_multilingual_sts_v2` - Multilingual speech-to-speech model (recommended)
- `eleven_english_sts_v2` - English-only speech-to-speech model

### Available Output Formats

- `mp3_44100_128` - MP3 at 44.1kHz, 128kbps (recommended)
- `mp3_44100_192` - MP3 at 44.1kHz, 192kbps
- `mp3_22050_32` - MP3 at 22.05kHz, 32kbps
- `pcm_16000` - PCM at 16kHz
- `pcm_22050` - PCM at 22.05kHz
- `pcm_24000` - PCM at 24kHz
- `pcm_44100` - PCM at 44.1kHz
- `ulaw_8000` - uLaw at 8kHz

## Getting Your ElevenLabs API Key

1. Go to [ElevenLabs](https://elevenlabs.io)
2. Create an account or sign in
3. Navigate to your profile settings
4. Copy your API key

## Getting Voice IDs

You can find voice IDs in the ElevenLabs Voice Library or create your own voices.

Default voice ID: `JBFqnCBsd6RMkjVDRZzb` (George)

## Example Workflow

1. Load an audio file using a "Load Audio" node
2. Connect it to the "ElevenLabs Voice Changer" node
3. Enter your API key and desired voice ID
4. Connect the output to a "Save Audio" or "Preview Audio" node

## Environment Variables

You can set your API key as an environment variable instead of entering it in the node:

```bash
export ELEVENLABS_API_KEY="your-api-key-here"
```

## License

MIT License

## Credits

- [ElevenLabs](https://elevenlabs.io) for the Speech-to-Speech API
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) for the node framework

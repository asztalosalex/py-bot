# Discord Bot

A Discord bot built with `discord.py`, combining an OpenAI-powered chat/image assistant with a YouTube music player and ElevenLabs text-to-speech.

## Features

- **AI chat** — mention the bot in a channel to chat with it; keeps the last 10 messages of conversation history per channel.
- **Image generation** — `!draw <prompt>` generates an image (DALL·E) and replies with it as an embed.
- **Voice greetings** — when a member joins a voice channel, the bot generates a short spoken greeting (OpenAI for the text, ElevenLabs for the audio) and plays it.
- **Music playback** — queue and play audio from YouTube via `yt-dlp`, including playlists.
- **Idle goodbye** — if the bot is alone in a voice channel with nothing queued, it says goodbye (TTS) and disconnects.

### Commands

| Command | Description |
|---|---|
| `!draw <prompt>` | Generate an image from a text prompt |
| `!join` | Join your current voice channel |
| `!leave` / `!disconnect` | Leave the voice channel |
| `!play <query or URL>` | Queue a song or playlist from YouTube |
| `!pause` / `!resume` | Pause/resume playback |
| `!skip` | Skip the current song |
| `!stop` | Stop playback and clear the queue |
| `!queue` | Show what's currently playing and queued |
| `!shuffle` | Shuffle the queue |

Mentioning the bot (`@botname <message>`) triggers a normal AI chat reply instead of a slash command.

## Tech stack

- Python 3.13, `discord.py` (voice extras)
- OpenAI API (chat + image generation)
- ElevenLabs API (text-to-speech)
- `yt-dlp` + `ffmpeg` for audio streaming
- `uv` for dependency management
- Docker
- pytest for unit tests
- GitHub Actions for CI/CD (SSH + rsync deploy to a VPS on push to `main`)

## Project structure

```
discord-bot-python/
├── main.py                  # Entry point
├── bot/
│   ├── discord_init.py       # Bot class, voice-join greeting/goodbye logic
│   └── cogs/
│       ├── ai_handler.py      # AI chat + !draw command
│       ├── music.py           # Music playback commands
│       └── basic_commands.py  # (currently unused/empty cog)
├── openai_service/
│   └── ai_init.py            # OpenAI client wrapper (chat, image, greeting text)
├── tts/
│   └── tts.py                 # ElevenLabs text-to-speech wrapper
├── tests/                    # pytest unit tests
└── Dockerfile
```

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- `ffmpeg` installed and on `PATH` (required for voice playback)
- A Discord bot token, an OpenAI API key, and an ElevenLabs API key

### Environment variables

Copy `.env.example` to `.env` and fill in your keys:

```env
DC_TOKEN=
OPENAI_KEY=
OPENAI_ORGANIZATION=
ELEVENLABS_API_KEY=
```

### Running locally

```bash
uv sync
uv run main.py
```

### Running tests

```bash
uv sync
uv run pytest
```

### Docker

```bash
docker build -t discord-bot-python .
docker run --env-file .env discord-bot-python
```

## Deployment

`.github/workflows/deploy.yml` deploys to a VPS via SSH/rsync on every push to `main`, restarting a `systemd` service on the target host. Configured through repository secrets (`SSH_PRIVATE_KEY`, `VPS_HOST`, `VPS_USERNAME`, `DEPLOY_PATH`, `SERVICE_NAME`, etc.) — no secrets are stored in the repo itself.

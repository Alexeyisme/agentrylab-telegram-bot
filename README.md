# AgentryLab Telegram Bot

A Telegram bot that provides access to AgentryLab's multi-agent conversations through an intuitive chat interface.

## Features

- **Preset Selection**: Choose from various conversation types (debates, stand-up, therapy, etc.)
- **Real-time Conversations**: Watch AI agents interact in real-time
- **User Participation**: Join conversations when it's your turn
- **Conversation Controls**: Pause, resume, stop, and view history
- **Rich UI**: Inline keyboards and formatted messages

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Bot**:
   ```bash
   cp config.example.py config.py
   # Edit config.py with your bot token and AgentryLab path
   ```

3. **Run Bot**:
   ```bash
   python bot/main.py
   ```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │  AgentryLab API  │    │  AgentryLab     │
│   (This Project)│◄──►│  (Thin Adapter)  │◄──►│  (Core Engine)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Project Structure

```
agentrylab-telegram-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py              # Bot entry point
│   ├── handlers/            # Message handlers
│   │   ├── __init__.py
│   │   ├── start.py         # /start command
│   │   ├── conversation.py  # Conversation handling
│   │   └── admin.py         # Admin commands
│   ├── keyboards/           # Inline keyboards
│   │   ├── __init__.py
│   │   ├── presets.py       # Preset selection
│   │   └── controls.py      # Conversation controls
│   ├── states/              # Conversation states
│   │   ├── __init__.py
│   │   └── conversation.py  # Conversation state management
│   └── utils/               # Helper functions
│       ├── __init__.py
│       ├── formatting.py    # Message formatting
│       └── validation.py    # Input validation
├── tests/                   # Test files
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
├── config.py               # Bot configuration
├── config.example.py       # Configuration template
└── README.md               # This file
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black bot/ tests/
flake8 bot/ tests/
```

## License

MIT License - see LICENSE file for details.


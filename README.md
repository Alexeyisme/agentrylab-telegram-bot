# 🤖 AgentryLab Telegram Bot

A Telegram bot that provides access to AgentryLab's multi-agent conversations through an intuitive chat interface.

[![Status](https://img.shields.io/badge/Status-Ready-brightgreen)](CHANGELOG.md)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)](tests/)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

## Features

- 🎭 **Preset Selection** - Choose conversation types (debates, therapy, brainstorming)
- 💬 **Real-time Conversations** - Watch AI agents interact live
- 👤 **User Participation** - Join conversations when it's your turn
- 🎮 **Conversation Controls** - Pause, resume, stop conversations
- 🔒 **Secure** - Input validation and content filtering

## Quick Start

### Prerequisites
- Python 3.8+
- AgentryLab instance
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- OpenAI API key for GPT models

### Installation
```bash
git clone https://github.com/Alexeyisme/agentrylab-telegram-bot.git
cd agentrylab-telegram-bot
./install.sh
source venv/bin/activate
```

### Configuration
```bash
cp env.example .env
# Edit .env with your bot token and settings (OPENAI_API_KEY is required)
```

### Run
```bash
python bot/main.py
```

### Test
Send `/start` to your bot on Telegram and follow the preset selection flow.

## Docker Deployment

```bash
# Build and run with Docker
docker-compose up -d

# Or use the deployment script
./deploy.sh

# Confirm the OpenAI credentials made it into the container
docker-compose exec agentrybot printenv | grep OPENAI
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Configuration

Key environment variables:
```bash
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORGANIZATION=your_openai_organization_id  # optional
AGENTRYLAB_PRESETS_PATH=/path/to/custom/presets   # optional
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_validation.py -v
```

## Documentation

- [Architecture](ARCHITECTURE.md) - Clean, simplified system design
- [Deployment](DEPLOYMENT.md) - Production deployment guide
- [Roadmap](ROADMAP.md) - Future development plans
- [Contributing](CONTRIBUTING.md) - How to contribute
- [Security](SECURITY.md) - Security policy
- [Changelog](CHANGELOG.md) - Version history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- [GitHub Issues](https://github.com/Alexeyisme/agentrylab-telegram-bot/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/Alexeyisme/agentrylab-telegram-bot/discussions) - Community discussions

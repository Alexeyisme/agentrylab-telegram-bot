# 🚀 Deployment Guide

## Prerequisites
- Ubuntu 20.04+ server
- SSH access
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- AgentryLab installation

## Quick Deployment

### 1. Connect to Server
```bash
ssh root@YOUR_SERVER_IP
```

### 2. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Create Application Directory
```bash
sudo mkdir -p /app
cd /app
```

### 4. Clone Telegram Bot Repository
```bash
# Clone Telegram Bot
git clone https://github.com/Alexeyisme/agentrylab-telegram-bot.git
cd agentrylab-telegram-bot
cp env.example .env
nano .env  # Edit with your bot token and OPENAI_API_KEY
```

### 5. Deploy Bot
```bash
./deploy.sh

# Confirm credentials made it into the container
docker-compose exec agentrybot printenv | grep OPENAI
```

### 6. Test
```bash
docker-compose logs -f agentrybot
```

Send `/start` to your bot on Telegram.

## Configuration

Edit `.env` file:
```bash
BOT_TOKEN=your_telegram_bot_token_here
BOT_USERNAME=your_bot_username
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORGANIZATION=your_openai_organization_id  # optional
AGENTRYLAB_PRESETS_PATH=/path/to/custom/presets   # optional
```

**Directory Structure:**
```
/app/
└── agentrylab-telegram-bot/       # Telegram bot
    ├── .env                       # Configuration
    ├── docker-compose.yml         # Deployment
    └── ...
```

**Note:** AgentryLab is now installed from PyPI (v0.1.6+) as a Python package, no need for separate cloning.

## Common Commands

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f agentrybot

# Restart bot
docker-compose restart agentrybot

# Stop bot
docker-compose down

# Update bot
git pull && docker-compose up -d
```

## Troubleshooting

### Bot Not Starting
```bash
# Check logs
docker-compose logs agentrybot

# Check configuration
cat .env
```

### Permission Issues
```bash
sudo chown -R $USER:$USER .
```

### AgentryLab Import Issues
```bash
# Check if AgentryLab is installed
docker-compose exec agentrybot python -c "import agentrylab; print(agentrylab.__version__)"

# If import fails, rebuild the container
docker-compose down
docker-compose up -d --build
```

## Security (Optional)

### Firewall
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Non-root User
```bash
adduser botuser
usermod -aG docker botuser
su - botuser
# Deploy as botuser
```

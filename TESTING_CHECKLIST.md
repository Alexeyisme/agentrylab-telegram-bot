# 🧪 Bot Testing Checklist

## ✅ Pre-Testing Setup

- [ ] Bot is deployed and running
- [ ] OpenAI API key is configured
- [ ] Bot token is set correctly
- [ ] Container is healthy: `docker-compose ps`

## 🚀 Basic Functionality Tests

### 1. Bot Connection
- [ ] Find bot in Telegram by username
- [ ] Send `/start` command
- [ ] Bot responds with welcome message
- [ ] Preset selection menu appears

### 2. Preset Selection
- [ ] All presets are visible (Debates, Therapy, Brainstorming)
- [ ] Tap on "Debates" preset
- [ ] Bot asks for topic input
- [ ] Tap on "Therapy" preset  
- [ ] Bot asks for topic input
- [ ] Tap on "Brainstorming" preset
- [ ] Bot asks for topic input

### 3. Topic Input
- [ ] Enter a simple topic: "AI ethics"
- [ ] Bot shows topic confirmation
- [ ] "Start Conversation" button appears
- [ ] Tap "Start Conversation"

### 4. Conversation Flow
- [ ] AI agents start responding
- [ ] Messages appear in real-time
- [ ] Wait for "your turn" message
- [ ] Send a response when prompted
- [ ] Conversation continues

## 🎮 Command Testing

### Basic Commands
- [ ] `/help` - Shows help message
- [ ] `/presets` - Shows preset selection
- [ ] `/status` - Shows current status
- [ ] `/start` - Resets to beginning

### Conversation Control
- [ ] `/pause` - Pauses active conversation
- [ ] `/resume` - Resumes paused conversation
- [ ] `/stop` - Stops conversation and resets

## 🔍 Error Handling Tests

### Invalid Input
- [ ] Send empty message
- [ ] Send very long message (>4000 chars)
- [ ] Send special characters only
- [ ] Send command during conversation

### Edge Cases
- [ ] Send `/start` during active conversation
- [ ] Send `/pause` when not in conversation
- [ ] Send `/resume` when not paused
- [ ] Send `/stop` when not in conversation

## 📊 Performance Tests

### Response Time
- [ ] Bot responds to `/start` within 2 seconds
- [ ] Preset selection appears within 1 second
- [ ] Topic confirmation appears within 1 second
- [ ] AI agents start responding within 10 seconds

### Conversation Quality
- [ ] AI responses are relevant to topic
- [ ] Multiple agents participate
- [ ] Conversation flows naturally
- [ ] User turn detection works correctly

## 🐛 Common Issues to Check

### Bot Not Responding
- [ ] Check container logs: `docker-compose logs -f agentrybot`
- [ ] Verify bot token is correct
- [ ] Check if OpenAI API key is set
- [ ] Restart container if needed

### Import Errors
- [ ] Check if AgentryLab is installed: `docker-compose exec agentrybot python -c "import agentrylab; print(agentrylab.__version__)"`
- [ ] Verify TelegramAdapter import: `docker-compose exec agentrybot python -c "from agentrylab.telegram import TelegramAdapter"`

### Conversation Issues
- [ ] Check if OpenAI API key is working
- [ ] Verify preset files are accessible
- [ ] Check conversation state management

## 📝 Test Results Template

```
Test Date: ___________
Bot Version: ___________
Tester: ___________

Basic Functionality: ✅/❌
Preset Selection: ✅/❌
Topic Input: ✅/❌
Conversation Flow: ✅/❌
Commands: ✅/❌
Error Handling: ✅/❌
Performance: ✅/❌

Issues Found:
- Issue 1: ___________
- Issue 2: ___________
- Issue 3: ___________

Overall Status: ✅ Working / ❌ Issues Found
```

## 🚀 Quick Test Script

Run this on your droplet to check basic functionality:

```bash
# Check container status
docker-compose ps

# Check logs for errors
docker-compose logs --tail=50 agentrybot

# Test AgentryLab import
docker-compose exec agentrybot python -c "import agentrylab; print('AgentryLab version:', agentrylab.__version__)"

# Test TelegramAdapter import
docker-compose exec agentrybot python -c "from agentrylab.telegram import TelegramAdapter; print('TelegramAdapter imported successfully')"
```

---

**Happy Testing!** 🎉

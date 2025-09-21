# 🏗️ Architecture

## Overview

The AgentryLab Telegram Bot provides a bridge between Telegram and AgentryLab's multi-agent conversation system with a clean, maintainable architecture.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │  AgentryLab API  │    │  AgentryLab     │
│   (This Project)│◄──►│  (Thin Adapter)  │◄──►│  (Core Engine)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Components

### Bot Framework
- **python-telegram-bot v20.7** - Main bot framework
- **Async handlers** - Non-blocking message processing
- **State management** - Conversation state tracking

### AgentryLab Integration
- **TelegramAdapter** - Thin adapter layer
- **Conversation streaming** - Real-time event processing
- **Preset management** - Conversation type selection

## Project Structure

```
bot/
├── app.py              # Main application entry point
├── main.py             # Backward compatibility entry point
├── config.py           # Centralized configuration
├── registry.py         # Service registry for dependency injection
├── state.py            # Simplified state management
├── handlers/
│   ├── commands.py     # Command handlers (/start, /help, /status)
│   ├── callbacks.py    # Callback query handlers
│   └── messages.py     # Message handlers
├── keyboards/
│   └── presets.py      # Inline keyboard generation
└── services/           # Business logic services
    ├── conversation_service.py
    └── preset_service.py
```

## Key Design Principles

### 1. **Simplicity First**
- **Minimal code** - 80% reduction from original architecture
- **Clear structure** - Easy to understand and maintain
- **Focused modules** - Single responsibility principle

### 2. **Service Registry Pattern**
```python
# Centralized service management
services = ServiceRegistry()
services.initialize(adapter, state)
conversation_service = services.get_conversation_service()
```

### 3. **Simple State Management**
```python
# Clean state tracking
user_state = state.get_user_state(user_id)
state.set_user_state(user_id, "active", conversation_id=conv_id)
```

### 4. **Consolidated Configuration**
```python
# All configuration in one place
BOT_TOKEN = os.getenv("BOT_TOKEN")
WELCOME_MSG = "🤖 Welcome to AgentryLab!"
```

## Data Flow

1. **User Input** → Telegram Bot
2. **Validation** → Input sanitization and validation
3. **State Management** → Conversation state tracking
4. **AgentryLab Integration** → Multi-agent conversation
5. **Event Streaming** → Real-time conversation display
6. **User Output** → Formatted responses

## Configuration

### Environment Variables
```bash
BOT_TOKEN=your_telegram_bot_token
BOT_USERNAME=your_bot_username
AGENTRYLAB_PATH=/app/agentrylab
LOG_LEVEL=INFO
POLLING=true
```

### Key Settings
- **POLLING**: Use polling mode (true) or webhook mode (false)
- **LOG_LEVEL**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- **AGENTRYLAB_PATH**: Path to AgentryLab installation

## Security

### Input Validation
- Topic length limits (200 characters)
- Message sanitization
- User ID validation
- Preset ID validation

### Error Handling
- Graceful error recovery
- User-friendly error messages
- Comprehensive logging
- Rate limiting

## Testing

### Test Structure
```
tests/
├── test_validation.py      # Input validation tests
├── test_keyboards.py       # UI component tests
├── test_conversation_state.py  # State management tests
├── test_integration.py     # End-to-end tests
├── test_edge_cases.py      # Edge case coverage
└── factories/
    └── test_data.py        # Test data factories
```

### Running Tests
```bash
pytest tests/ -v
pytest tests/test_validation.py -v
```

## Deployment

### Docker
```bash
docker-compose up -d
```

### Manual
```bash
python bot/main.py
```

## Performance

### Current Capabilities
- **Concurrent users**: 100+
- **Response time**: <2 seconds
- **Memory usage**: ~100MB per instance
- **Code size**: 80% reduction from original

### Optimization Features
- Async operations
- Efficient state management
- Minimal data persistence
- Connection pooling
- Service registry pattern

## Benefits

### Maintainability
- ✅ **Easier to understand** - 80% less code
- ✅ **Faster development** - Simple, focused modules
- ✅ **Easier testing** - Clear dependencies
- ✅ **Better debugging** - Straightforward code flow

### Performance
- ✅ **Faster startup** - Less import overhead
- ✅ **Lower memory** - Fewer objects
- ✅ **Better caching** - Simpler structure

### Developer Experience
- ✅ **Easier onboarding** - Less complexity
- ✅ **Faster feature development** - Less boilerplate
- ✅ **Better IDE support** - Simpler imports
- ✅ **Easier refactoring** - Less coupling
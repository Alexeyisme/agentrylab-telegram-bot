# 🔧 Refactoring Plan: AgentryLab Telegram Bot

## 🎯 **Priority 1: Error Handling Simplification**

### **Current Problem**
Repetitive error handling code appears 20+ times:
```python
try:
    # operation
except Exception as e:
    logger.error(f"Error: {e}")
    await update.message.reply_text("❌ Error message")
```

### **Solution: Error Handling Decorator**
```python
# bot/utils/error_handling.py
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def handle_errors(error_message: str = "An error occurred. Please try again."):
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            try:
                return await func(update, context, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                await update.message.reply_text(f"❌ {error_message}")
        return wrapper
    return decorator
```

### **Usage Example**
```python
@handle_errors("Error starting conversation. Please try again.")
async def start_conversation_with_agentrylab(update, context, preset_id, topic):
    # Implementation without try/catch
    adapter = get_adapter(context)
    conversation_id = adapter.start_conversation(preset_id, topic, user_id)
    return conversation_id
```

---

## 🎯 **Priority 2: Constants and Configuration**

### **Current Problem**
Magic strings scattered throughout code:
- `"❌ Bot not properly initialized. Please try again later."` (8+ times)
- `"preset_"`, `"select_"`, `"examples_"` (callback prefixes)

### **Solution: Constants Module**
```python
# bot/constants.py
class Messages:
    BOT_NOT_INITIALIZED = "❌ Bot not properly initialized. Please try again later."
    NO_ACTIVE_CONVERSATION = "❌ You don't have an active conversation."
    ERROR_OCCURRED = "❌ An error occurred. Please try again later."
    CONVERSATION_STARTED = "🚀 **Conversation Started!**"
    USER_TURN = "👤 **It's your turn!** What would you like to say?"

class CallbackPrefixes:
    PRESET = "preset_"
    SELECT = "select_"
    EXAMPLES = "examples_"
    CUSTOM = "custom_"
    START = "start_"
    EDIT = "edit_"

class ConversationStates:
    IDLE = "idle"
    SELECTING_PRESET = "selecting_preset"
    ENTERING_TOPIC = "entering_topic"
    CONFIRMING_TOPIC = "confirming_topic"
    IN_CONVERSATION = "in_conversation"
    WAITING_FOR_USER_INPUT = "waiting_for_user_input"
    CONVERSATION_PAUSED = "conversation_paused"
    CONVERSATION_ENDED = "conversation_ended"
    ERROR = "error"
```

---

## 🎯 **Priority 3: Callback Router Pattern**

### **Current Problem**
`handle_preset_callback` function has 15+ different callback types in one function.

### **Solution: Callback Router**
```python
# bot/handlers/callback_router.py
class CallbackRouter:
    def __init__(self):
        self.handlers = {}
    
    def register(self, prefix: str, handler_func):
        self.handlers[prefix] = handler_func
    
    async def handle_callback(self, update, context):
        query = update.callback_query
        data = query.data
        
        for prefix, handler in self.handlers.items():
            if data.startswith(prefix):
                callback_data = data.replace(prefix, "", 1)
                return await handler(query, context, callback_data)
        
        await query.edit_message_text("❌ Unknown action. Please try again.")

# Usage in main.py
router = CallbackRouter()
router.register(CallbackPrefixes.PRESET, show_preset_info)
router.register(CallbackPrefixes.SELECT, start_topic_input)
router.register(CallbackPrefixes.EXAMPLES, show_preset_examples)
```

---

## 🎯 **Priority 4: Service Layer Implementation**

### **Current Problem**
Business logic mixed with presentation logic in handlers.

### **Solution: Service Layer**
```python
# bot/services/conversation_service.py
class ConversationService:
    def __init__(self, adapter, state_manager):
        self.adapter = adapter
        self.state_manager = state_manager
    
    async def start_conversation(self, user_id: str, preset_id: str, topic: str) -> str:
        """Start a new conversation."""
        conversation_id = self.adapter.start_conversation(preset_id, topic, user_id)
        self.state_manager.set_user_conversation_id(user_id, conversation_id)
        self.state_manager.set_user_state(user_id, ConversationState.IN_CONVERSATION)
        return conversation_id
    
    async def handle_user_input(self, user_id: str, message: str) -> bool:
        """Handle user input during conversation."""
        user_state = self.state_manager.get_user_state(user_id)
        if user_state.state != ConversationState.WAITING_FOR_USER_INPUT:
            return False
        
        self.adapter.post_user_message(user_state.conversation_id, message, user_id)
        self.state_manager.set_user_state(user_id, ConversationState.IN_CONVERSATION)
        return True
```

---

## 🎯 **Priority 5: Context Helpers**

### **Current Problem**
Adapter retrieval repeated 20+ times:
```python
adapter = context.bot_data.get('adapter')
if not adapter:
    await update.message.reply_text("❌ Bot not properly initialized...")
    return
```

### **Solution: Context Helpers**
```python
# bot/utils/context_helpers.py
from bot.constants import Messages

class BotNotInitializedError(Exception):
    pass

def get_adapter(context) -> TelegramAdapter:
    """Get adapter from context with validation."""
    adapter = context.bot_data.get('adapter')
    if not adapter:
        raise BotNotInitializedError("Bot not properly initialized")
    return adapter

async def require_adapter(update, context) -> TelegramAdapter:
    """Get adapter or send error message."""
    try:
        return get_adapter(context)
    except BotNotInitializedError:
        await update.message.reply_text(Messages.BOT_NOT_INITIALIZED)
        raise

async def require_active_user(update, context) -> UserConversationState:
    """Get user state or send error message if not active."""
    user_id = str(update.effective_user.id)
    user_state = state_manager.get_user_state(user_id)
    
    if not user_state.is_active():
        await update.message.reply_text(Messages.NO_ACTIVE_CONVERSATION)
        raise UserNotActiveError("User has no active conversation")
    
    return user_state
```

---

## 🎯 **Priority 6: Message Templates**

### **Current Problem**
Message formatting logic repeated throughout handlers.

### **Solution: Message Templates**
```python
# bot/templates/messages.py
class MessageTemplates:
    @staticmethod
    def preset_confirmation(emoji: str, display_name: str, topic: str) -> str:
        return f"""{emoji} **{display_name}**

**Topic:** {topic}

Ready to start the conversation? Click below to begin!"""
    
    @staticmethod
    def conversation_started() -> str:
        return """🚀 **Conversation Started!**

The AI agents are now discussing your topic. 
You'll see their messages in real-time below.

---"""
    
    @staticmethod
    def user_turn_prompt() -> str:
        return """👤 **It's your turn!** What would you like to say?

Type your message below:"""
    
    @staticmethod
    def conversation_completed() -> str:
        return """✅ **Conversation Completed!**

The discussion has ended. Thank you for participating!

Use /start to begin a new conversation."""
```

---

## 🎯 **Priority 7: Preset Service**

### **Current Problem**
Preset information retrieval duplicated 4+ times.

### **Solution: Preset Service**
```python
# bot/services/preset_service.py
class PresetService:
    def __init__(self, adapter):
        self.adapter = adapter
    
    async def get_preset_info_batch(self, preset_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get information for multiple presets with error handling."""
        preset_info = {}
        for preset_id in preset_ids:
            preset_info[preset_id] = await self._get_single_preset_info(preset_id)
        return preset_info
    
    async def _get_single_preset_info(self, preset_id: str) -> Dict[str, Any]:
        """Get information for a single preset with fallback."""
        try:
            info = self.adapter.get_preset_info(preset_id)
            return {
                'display_name': get_preset_display_name(preset_id),
                'description': get_preset_description(preset_id),
                'emoji': get_preset_emoji(preset_id),
                'category': info.get('category', 'Other'),
                'examples': get_preset_examples(preset_id)
            }
        except Exception as e:
            logger.warning(f"Could not get info for preset {preset_id}: {e}")
            return self._get_fallback_preset_info(preset_id)
    
    def _get_fallback_preset_info(self, preset_id: str) -> Dict[str, Any]:
        """Get fallback preset information."""
        return {
            'display_name': get_preset_display_name(preset_id),
            'description': get_preset_description(preset_id),
            'emoji': get_preset_emoji(preset_id),
            'category': 'Other',
            'examples': get_preset_examples(preset_id)
        }
```

---

## 🎯 **Priority 8: Test Data Factories**

### **Current Problem**
Test data hardcoded and duplicated across test files.

### **Solution: Test Data Factories**
```python
# tests/factories/test_data.py
class TestDataFactory:
    @staticmethod
    def create_user_state(user_id: str = "123456789", 
                         state: ConversationState = ConversationState.IDLE) -> UserConversationState:
        return UserConversationState(
            user_id=user_id,
            state=state,
            selected_preset="debates",
            selected_topic="Test topic"
        )
    
    @staticmethod
    def create_preset_info(preset_id: str = "debates") -> Dict[str, Any]:
        return {
            'display_name': 'Debates',
            'description': 'Structured debates with AI agents',
            'emoji': '⚖️',
            'category': 'Discussion',
            'examples': ['Should remote work become the standard?']
        }
    
    @staticmethod
    def create_conversation_event(event_type: str = "agent_message") -> ConversationEvent:
        return ConversationEvent(
            conversation_id="test-conversation-id",
            event_type=event_type,
            content="Test message content",
            metadata={}
        )
```

---

## 📊 **Implementation Timeline**

### **Week 1: Core Refactoring**
- [ ] Implement error handling decorator
- [ ] Create constants module
- [ ] Implement context helpers
- [ ] Add message templates

### **Week 2: Architecture Improvements**
- [ ] Implement callback router
- [ ] Add service layer
- [ ] Create preset service
- [ ] Refactor handlers

### **Week 3: Testing & Validation**
- [ ] Add test data factories
- [ ] Implement integration tests
- [ ] Add edge case testing
- [ ] Update existing tests

### **Week 4: Documentation & Cleanup**
- [ ] Update documentation
- [ ] Code review and cleanup
- [ ] Performance testing
- [ ] Final validation

---

## 🎯 **Expected Results**

### **Code Quality Metrics**
- **50% reduction** in code duplication
- **30% reduction** in function complexity
- **80% reduction** in repetitive error handling
- **100% consistent** error handling patterns

### **Maintainability Improvements**
- **Easier debugging** with centralized error handling
- **Faster development** with reusable components
- **Better code navigation** with clear architecture
- **Improved testability** with service layer separation

### **Performance Benefits**
- **Faster error handling** with decorators
- **Reduced memory usage** with optimized state management
- **Better scalability** with async operations
- **Improved response times** with streamlined code paths

---

## 🚀 **Next Steps**

1. **Start with Priority 1** - Error handling decorator (highest impact, lowest effort)
2. **Implement incrementally** - One priority at a time
3. **Maintain test coverage** - Update tests as you refactor
4. **Document changes** - Update documentation for new patterns
5. **Code review** - Ensure quality and consistency

This refactoring plan will transform the codebase from a functional prototype to a production-ready, maintainable system while preserving all existing functionality.

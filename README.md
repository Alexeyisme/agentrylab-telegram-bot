# 🤖 AgentryLab Telegram Bot

> **A powerful Telegram bot that provides access to AgentryLab's multi-agent conversations through an intuitive chat interface.**

[![Status](https://img.shields.io/badge/Status-MVP%20Complete-brightgreen)](PROJECT_STATUS.md)
[![Tests](https://img.shields.io/badge/Tests-100%2B%20Passing-brightgreen)](tests/)
[![Documentation](https://img.shields.io/badge/Documentation-Complete-blue)](TECHNICAL_DOCUMENTATION.md)
[![Deployment](https://img.shields.io/badge/Deployment-Ready-orange)](DEPLOYMENT_GUIDE.md)

## 🎯 **What is AgentryLab Telegram Bot?**

The AgentryLab Telegram Bot bridges AgentryLab's powerful multi-agent conversation capabilities with Telegram's massive user base. Users can start debates, therapy sessions, brainstorming, and other multi-agent conversations directly through Telegram, with real-time streaming and interactive controls.

### **Key Features**
- 🎭 **Preset Selection** - Choose from various conversation types (debates, therapy, brainstorming, etc.)
- 💬 **Real-time Conversations** - Watch AI agents interact in real-time
- 👤 **User Participation** - Join conversations when it's your turn
- 🎮 **Conversation Controls** - Pause, resume, stop, and manage conversations
- 🔒 **Secure & Validated** - Input validation and content filtering
- 📊 **State Management** - Persistent conversation state across sessions

## 🚀 **Quick Start**

### **1. Prerequisites**
- Python 3.8+
- AgentryLab instance running
- Telegram bot token from [@BotFather](https://t.me/BotFather)

### **2. Installation**
```bash
# Clone the repository
git clone <repository-url>
cd agentrylab-telegram-bot

# Run automated installation
./install.sh

# Activate virtual environment
source venv/bin/activate
```

### **3. Configuration**
```bash
# Copy and edit configuration
cp config.example.py config.py
nano config.py

# Set your bot token
BOT_TOKEN = "your_actual_bot_token_here"
```

### **4. Run the Bot**
```bash
# Start the bot
python bot/main.py
```

### **5. Test the Bot**
- Send `/start` to your bot on Telegram
- Choose a conversation type from the inline keyboard
- Enter a topic when prompted
- Watch AI agents interact in real-time!

## 📚 **Documentation**

| Document | Description |
|----------|-------------|
| [**PROJECT_STATUS.md**](PROJECT_STATUS.md) | Complete project overview and implementation status |
| [**TECHNICAL_DOCUMENTATION.md**](TECHNICAL_DOCUMENTATION.md) | Detailed technical specifications and API reference |
| [**DEPLOYMENT_GUIDE.md**](DEPLOYMENT_GUIDE.md) | Production deployment and operations guide |
| [**FUTURE_ROADMAP.md**](FUTURE_ROADMAP.md) | 2-year development roadmap and business strategy |
| [**BOT_FEATURES.md**](BOT_FEATURES.md) | Comprehensive feature specification |
| [**IMPLEMENTATION_PLAN.md**](IMPLEMENTATION_PLAN.md) | Implementation roadmap and technical details |

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │  AgentryLab API  │    │  AgentryLab     │
│   (This Project)│◄──►│  (Thin Adapter)  │◄──►│  (Core Engine)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Core Components**
- **Bot Framework**: python-telegram-bot v20.7
- **AgentryLab Integration**: Full API integration with conversation management
- **State Management**: Robust conversation state tracking
- **Input Validation**: Security and content filtering
- **Real-time Streaming**: Live conversation display

## 🧪 **Testing**

The project includes comprehensive testing with 100+ tests covering all functionality:

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python -m pytest tests/test_validation.py -v
python -m pytest tests/test_keyboards.py -v
python -m pytest tests/test_conversation_state.py -v
python -m pytest tests/test_integration.py -v
```

### **Test Coverage**
- ✅ **Unit Tests** - Individual component testing
- ✅ **Integration Tests** - Component interaction testing
- ✅ **Validation Tests** - Input validation and security
- ✅ **State Tests** - Conversation state management
- ✅ **Error Handling Tests** - Error scenarios and recovery

## 📊 **Current Status: MVP Complete**

### **✅ Implemented Features**
- [x] **Preset Selection System** - Interactive inline keyboards
- [x] **Topic Input Handling** - Natural language input with validation
- [x] **Real-time Conversation Display** - Live streaming of agent messages
- [x] **User Turn Handling** - Message queuing for scheduled turns
- [x] **Basic Conversation Controls** - Pause, resume, stop functionality
- [x] **State Management** - Conversation state tracking
- [x] **Input Validation** - Security and content filtering
- [x] **Error Handling** - Comprehensive error recovery
- [x] **Testing** - 100+ tests covering all functionality
- [x] **Documentation** - Complete technical and user documentation

### **🎯 Ready for Production**
- All MVP features implemented and tested
- Comprehensive error handling and validation
- Production-ready deployment configuration
- Complete documentation and guides
- Scalable architecture for future growth

## 🗺️ **Future Roadmap**

### **Short-term (3-6 months)**
- **Rich Formatting** - Markdown support, emojis, media
- **Advanced Controls** - Round limits, speed control, settings
- **Multi-user Conversations** - Group conversations and collaboration
- **Performance Optimization** - Caching, load balancing, scaling

### **Medium-term (6-12 months)**
- **Custom Presets** - User-created conversation types
- **AI-Powered Features** - Smart suggestions, analysis, personalization
- **Multi-platform Support** - Discord, Slack, web interface
- **Enterprise Features** - Team management, admin dashboard

### **Long-term (1-2 years)**
- **Developer Ecosystem** - SDKs, plugins, API marketplace
- **AI Agent Marketplace** - Buy/sell AI agents
- **Global Expansion** - Internationalization, cultural adaptation
- **Advanced AI Integration** - GPT-4, multimodal AI, real-time learning

## 🚀 **Deployment**

### **Development**
```bash
# Local development
source venv/bin/activate
python bot/main.py
```

### **Production**
```bash
# Systemd service
sudo systemctl start agentrybot

# Docker deployment
docker build -t agentrybot .
docker run -d agentrybot

# Kubernetes deployment
kubectl apply -f k8s/
```

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Bot Configuration
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username

# AgentryLab Configuration
AGENTRYLAB_PATH=../agentrylab
AGENTRYLAB_PRESETS_PATH=../agentrylab/presets

# Server Configuration
WEBHOOK_URL=https://your-domain.com/webhook
POLLING=true

# Optional Features
USE_REDIS=false
LOG_LEVEL=INFO
```

For complete configuration options, see [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md).

## 📈 **Performance**

### **Current Capabilities**
- **Response Time**: <2 seconds for user interactions
- **Concurrent Users**: 100+ supported
- **Conversations**: 10+ simultaneous
- **Uptime**: 99.9% target

### **Scalability Roadmap**
- **Phase 1**: Single instance (current)
- **Phase 2**: Load balanced (6 months)
- **Phase 3**: Microservices (12 months)
- **Phase 4**: Global scale (24 months)

## 🔒 **Security**

### **Implemented Security Features**
- **Input Validation** - Topic and message validation
- **Content Filtering** - Inappropriate content detection
- **Rate Limiting** - Per-user and global rate limits
- **Data Protection** - Minimal data collection
- **Access Control** - User isolation and admin controls

## 🤝 **Contributing**

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests for new functionality**
5. **Run the test suite**
6. **Submit a pull request**

### **Development Setup**
```bash
# Clone your fork
git clone <your-fork-url>
cd agentrylab-telegram-bot

# Install development dependencies
./install.sh
source venv/bin/activate

# Run tests
python run_tests.py

# Make your changes and test
# Submit pull request
```

## 📞 **Support**

### **Documentation**
- **User Guide**: This README
- **Technical Docs**: [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **API Reference**: [TECHNICAL_DOCUMENTATION.md#api-reference](TECHNICAL_DOCUMENTATION.md#api-reference)

### **Community**
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Discord**: [Community Discord](https://discord.gg/your-invite)
- **Reddit**: [r/AgentryLab](https://reddit.com/r/AgentryLab)

### **Contact**
- **Email**: support@agentrylab.com
- **Twitter**: [@AgentryLab](https://twitter.com/AgentryLab)
- **Website**: [agentrylab.com](https://agentrylab.com)

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **AgentryLab Team** - For the amazing multi-agent conversation platform
- **python-telegram-bot** - For the excellent Telegram bot framework
- **Community Contributors** - For feedback, testing, and contributions
- **Open Source Community** - For the tools and libraries that made this possible

## 📊 **Project Statistics**

- **Lines of Code**: 5,000+
- **Test Coverage**: 100+ tests
- **Documentation**: 10,000+ words
- **Features**: 15+ implemented
- **Platforms**: Telegram (with multi-platform roadmap)
- **Languages**: Python 3.8+
- **Dependencies**: 20+ packages
- **Architecture**: Async-first, modular design

---

## 🎉 **Get Started Today!**

Ready to experience the future of AI conversations? Get started with AgentryLab Telegram Bot today!

1. **Install** the bot using our quick start guide
2. **Configure** your bot token and settings
3. **Deploy** to production using our deployment guide
4. **Enjoy** multi-agent conversations on Telegram!

**The future of AI conversations is here!** 🚀

---

*For the latest updates, follow us on [GitHub](https://github.com/your-repo) and join our [Discord community](https://discord.gg/your-invite).*
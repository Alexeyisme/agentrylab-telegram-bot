# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite with 100+ tests
- Docker deployment support
- CI/CD pipeline with GitHub Actions
- Security scanning and vulnerability checks
- Simplified architecture with 80% code reduction

### Changed
- **Major Architecture Overhaul**: Simplified from 2,458 lines to 492 lines in core components
- **Service Registry Pattern**: Centralized dependency injection
- **Consolidated Configuration**: Single config file instead of multiple verbose files
- **Streamlined Handlers**: Focused, single-responsibility handlers
- **Simplified State Management**: Clean dataclass-based state tracking

### Fixed
- Critical syntax errors in handlers
- Import issues in services
- Context handling in main application
- Over-engineering and unnecessary complexity

## [1.0.0] - 2024-12-19

### Added
- Initial release of AgentryLab Telegram Bot
- Multi-agent conversation support
- Preset selection system
- Real-time conversation streaming
- User participation in conversations
- Conversation state management
- Input validation and sanitization
- Error handling and logging
- Docker deployment support
- Comprehensive documentation

### Features
- **Preset Selection**: Choose from various conversation types (debates, therapy, brainstorming, etc.)
- **Real-time Conversations**: Watch AI agents interact in real-time
- **User Participation**: Join conversations when it's your turn
- **Conversation Controls**: Pause, resume, stop, and manage conversations
- **State Management**: Persistent conversation state across sessions
- **Security**: Input validation and content filtering

### Technical
- Built with Python 3.8+
- Uses python-telegram-bot framework
- Integrates with AgentryLab core
- Supports both polling and webhook modes
- Docker containerization
- Comprehensive test coverage

## [0.9.0] - 2024-12-18

### Added
- MVP implementation
- Basic preset selection
- Topic input handling
- Conversation management
- State persistence

### Changed
- Initial architecture design
- Core functionality implementation

## [0.8.0] - 2024-12-17

### Added
- Project initialization
- Basic bot structure
- AgentryLab integration
- Telegram bot setup

### Changed
- Project structure planning
- Architecture design

---

## Version History

- **v1.0.0**: First stable release with full feature set
- **v0.9.0**: MVP with core functionality
- **v0.8.0**: Initial project setup and architecture

## Release Notes

### v1.0.0 Release Notes
This is the first stable release of AgentryLab Telegram Bot. It includes all core features for running multi-agent conversations through Telegram, with comprehensive testing, documentation, and deployment support.

**Key Features:**
- Complete preset selection system
- Real-time conversation streaming
- User participation and controls
- Docker deployment
- Comprehensive documentation

**Breaking Changes:**
- None (first stable release)

**Migration Guide:**
- N/A (first stable release)

### v0.9.0 Release Notes
MVP release with core functionality for basic bot operations.

**Key Features:**
- Basic preset selection
- Topic input handling
- Simple conversation management

### v0.8.0 Release Notes
Initial project setup with basic architecture and AgentryLab integration.

**Key Features:**
- Project structure
- Basic bot framework
- AgentryLab integration setup

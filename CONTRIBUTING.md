# Contributing to AgentryLab Telegram Bot

Thank you for your interest in contributing to AgentryLab Telegram Bot! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- AgentryLab instance
- Telegram bot token

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/agentrylab-telegram-bot.git
   cd agentrylab-telegram-bot
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run tests**
   ```bash
   pytest tests/ -v
   ```

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused

### Testing
- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Use descriptive test names

### Documentation
- Update documentation for new features
- Add examples for new functionality
- Keep README.md up to date

## 🔄 Workflow

### Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches
- `hotfix/*`: Critical bug fixes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**
   ```bash
   # Run linting
   flake8 bot/
   black --check bot/
   mypy bot/
   
   # Run tests
   pytest tests/ -v
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format
Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

## 🐛 Bug Reports

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs

## 💡 Feature Requests

When requesting features, please include:
- Clear description of the feature
- Use case and motivation
- Implementation ideas (if any)
- Priority level

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_validation.py -v

# Run with coverage
pytest tests/ --cov=bot --cov-report=html
```

### Writing Tests
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Use fixtures for common test data

## 📚 Code Review

### For Reviewers
- Be constructive and respectful
- Focus on code quality and functionality
- Check for security issues
- Verify tests are adequate

### For Authors
- Respond to feedback promptly
- Make requested changes
- Ask questions if feedback is unclear
- Keep PRs focused and small

## 🔒 Security

- Never commit sensitive information (tokens, passwords, etc.)
- Use environment variables for configuration
- Validate all user inputs
- Follow security best practices

## 📞 Getting Help

- Check existing issues and discussions
- Join our community discussions
- Create an issue for questions
- Contact maintainers for urgent issues

## 🎉 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to AgentryLab Telegram Bot! 🚀

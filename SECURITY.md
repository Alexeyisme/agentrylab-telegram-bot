# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. **DO NOT** create a public GitHub issue
Security vulnerabilities should be reported privately to prevent exploitation.

### 2. Email us directly
Send an email to: [security@agentrylab.com](mailto:security@agentrylab.com)

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline
- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution**: Within 30 days (depending on complexity)

### 4. Disclosure Process
- We will work with you to understand and resolve the issue
- Once fixed, we will credit you in our security advisories
- We will coordinate public disclosure timing with you

## Security Best Practices

### For Users
- Keep your bot token secure and never share it
- Use environment variables for sensitive configuration
- Regularly update to the latest version
- Monitor your bot's logs for suspicious activity
- Use strong, unique passwords for any admin accounts

### For Developers
- Never commit sensitive information to version control
- Validate all user inputs
- Use HTTPS for webhook endpoints
- Implement rate limiting
- Follow the principle of least privilege
- Keep dependencies updated

## Security Features

### Input Validation
- All user inputs are validated and sanitized
- Topic inputs are length-limited and filtered
- Message content is checked for malicious patterns

### Rate Limiting
- Built-in rate limiting for user interactions
- Conversation limits per user
- Message rate limiting

### Error Handling
- Secure error messages that don't leak sensitive information
- Proper exception handling throughout the codebase
- Logging without exposing sensitive data

### Authentication
- Bot token authentication with Telegram
- Admin user ID validation
- Secure session management

## Dependencies

We regularly audit our dependencies for security vulnerabilities:

```bash
# Check for known vulnerabilities
pip install safety
safety check

# Security linting
pip install bandit
bandit -r bot/
```

## Reporting Security Issues

If you find a security vulnerability, please report it responsibly:

1. **Email**: [security@agentrylab.com](mailto:security@agentrylab.com)
2. **Subject**: "Security Vulnerability in AgentryLab Telegram Bot"
3. **Include**: Detailed description and reproduction steps

## Security Updates

Security updates will be released as:
- **Patch versions** for critical vulnerabilities
- **Minor versions** for important security improvements
- **Security advisories** for significant issues

## Acknowledgments

We thank security researchers who responsibly disclose vulnerabilities. Contributors will be credited in our security advisories.

## Contact

For security-related questions or concerns:
- **Email**: [security@agentrylab.com](mailto:security@agentrylab.com)
- **Response Time**: Within 48 hours

Thank you for helping keep AgentryLab Telegram Bot secure! 🔒

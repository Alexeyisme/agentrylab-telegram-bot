# 🚀 AgentryLab Telegram Bot - Deployment & Operations Guide

## 📋 **Table of Contents**

1. [Quick Start](#quick-start)
2. [Production Deployment](#production-deployment)
3. [Environment Setup](#environment-setup)
4. [Configuration Management](#configuration-management)
5. [Monitoring & Logging](#monitoring--logging)
6. [Scaling & Performance](#scaling--performance)
7. [Security Hardening](#security-hardening)
8. [Backup & Recovery](#backup--recovery)
9. [Maintenance Procedures](#maintenance-procedures)
10. [Troubleshooting](#troubleshooting)

---

## ⚡ **Quick Start**

### **1. Prerequisites**
- Python 3.8+ installed
- AgentryLab instance running
- Telegram bot token from @BotFather
- Git installed

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

### **4. Run Bot**
```bash
# Start the bot
python bot/main.py
```

### **5. Test Bot**
- Send `/start` to your bot on Telegram
- Follow the preset selection flow
- Verify conversation functionality

---

## 🏭 **Production Deployment**

### **1. Server Requirements**

#### **Minimum Requirements**
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 20 GB SSD
- **Network**: 100 Mbps connection
- **OS**: Ubuntu 20.04+ or CentOS 8+

#### **Recommended Requirements**
- **CPU**: 4 cores, 3.0 GHz
- **RAM**: 8 GB
- **Storage**: 50 GB SSD
- **Network**: 1 Gbps connection
- **OS**: Ubuntu 22.04 LTS

### **2. System Setup**

#### **Ubuntu/Debian Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.12 python3.12-venv python3.12-dev git nginx

# Install Redis (optional)
sudo apt install -y redis-server

# Create bot user
sudo useradd -m -s /bin/bash agentrybot
sudo usermod -aG sudo agentrybot
```

#### **CentOS/RHEL Setup**
```bash
# Update system
sudo yum update -y

# Install Python and dependencies
sudo yum install -y python3.12 python3.12-venv python3.12-devel git nginx

# Install Redis (optional)
sudo yum install -y redis

# Create bot user
sudo useradd -m -s /bin/bash agentrybot
sudo usermod -aG wheel agentrybot
```

### **3. Application Deployment**

#### **Deploy Application**
```bash
# Switch to bot user
sudo su - agentrybot

# Clone repository
git clone <repository-url> /home/agentrybot/agentrylab-telegram-bot
cd /home/agentrybot/agentrylab-telegram-bot

# Install dependencies
./install.sh

# Set up configuration
cp config.example.py config.py
nano config.py
```

#### **Production Configuration**
```python
# config.py - Production settings
import os

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set via environment
BOT_USERNAME = os.getenv("BOT_USERNAME")

# AgentryLab Configuration
AGENTRYLAB_PATH = "/opt/agentrylab"  # Adjust path
AGENTRYLAB_PRESETS_PATH = "/opt/agentrylab/presets"

# Server Configuration
WEBHOOK_URL = "https://your-domain.com/webhook"
WEBHOOK_PORT = 8443
POLLING = False  # Use webhook in production

# Database Configuration
REDIS_URL = "redis://localhost:6379/0"
USE_REDIS = True  # Enable Redis for state persistence

# Rate Limiting
MAX_CONVERSATIONS_PER_USER = 5
MESSAGE_RATE_LIMIT = 20

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "/var/log/agentrybot/bot.log"

# Admin Configuration
ADMIN_USER_IDS = [123456789, 987654321]  # Your admin user IDs

# Feature Flags
ENABLE_CONVERSATION_HISTORY = True
ENABLE_ADMIN_COMMANDS = True
ENABLE_ANALYTICS = True

# Message Limits
MAX_MESSAGE_LENGTH = 4000
MAX_TOPIC_LENGTH = 200

# Timeouts
CONVERSATION_TIMEOUT = 7200  # 2 hours
USER_INPUT_TIMEOUT = 600     # 10 minutes
```

### **4. Systemd Service**

#### **Create Service File**
```bash
sudo nano /etc/systemd/system/agentrybot.service
```

#### **Service Configuration**
```ini
[Unit]
Description=AgentryLab Telegram Bot
After=network.target redis.service
Wants=redis.service

[Service]
Type=simple
User=agentrybot
Group=agentrybot
WorkingDirectory=/home/agentrybot/agentrylab-telegram-bot
Environment=PATH=/home/agentrybot/agentrylab-telegram-bot/venv/bin
ExecStart=/home/agentrybot/agentrylab-telegram-bot/venv/bin/python bot/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/agentrybot/agentrylab-telegram-bot
ReadWritePaths=/var/log/agentrybot

[Install]
WantedBy=multi-user.target
```

#### **Enable and Start Service**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable agentrybot

# Start service
sudo systemctl start agentrybot

# Check status
sudo systemctl status agentrybot
```

### **5. Nginx Configuration (Webhook Mode)**

#### **Install SSL Certificate**
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

#### **Nginx Configuration**
```nginx
# /etc/nginx/sites-available/agentrybot
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Webhook endpoint
    location /webhook {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

#### **Enable Nginx Configuration**
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/agentrybot /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

---

## 🌍 **Environment Setup**

### **1. Environment Variables**

#### **Production Environment**
```bash
# /etc/environment
BOT_TOKEN=your_production_bot_token
BOT_USERNAME=your_production_bot_username
AGENTRYLAB_PATH=/opt/agentrylab
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
```

#### **Development Environment**
```bash
# .env file
BOT_TOKEN=your_development_bot_token
BOT_USERNAME=your_development_bot_username
AGENTRYLAB_PATH=../agentrylab
REDIS_URL=redis://localhost:6379/1
LOG_LEVEL=DEBUG
```

### **2. Directory Structure**

#### **Production Layout**
```
/opt/agentrylab-telegram-bot/
├── bot/                    # Application code
├── config.py              # Configuration
├── requirements.txt        # Dependencies
├── venv/                  # Virtual environment
├── logs/                  # Log files
├── data/                  # Persistent data
└── backups/               # Backup files
```

#### **Log Directory Setup**
```bash
# Create log directory
sudo mkdir -p /var/log/agentrybot
sudo chown agentrybot:agentrybot /var/log/agentrybot
sudo chmod 755 /var/log/agentrybot
```

### **3. Redis Configuration (Optional)**

#### **Redis Setup**
```bash
# Install Redis
sudo apt install -y redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
```

#### **Redis Configuration**
```conf
# /etc/redis/redis.conf
bind 127.0.0.1
port 6379
timeout 300
tcp-keepalive 60

# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
```

#### **Start Redis**
```bash
# Enable and start Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

---

## ⚙️ **Configuration Management**

### **1. Configuration Validation**

#### **Validation Script**
```python
# scripts/validate_config.py
import sys
import os
sys.path.insert(0, '.')

from config import *
from bot.utils.validation import validate_user_id

def validate_config():
    """Validate configuration settings."""
    errors = []
    
    # Check required settings
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        errors.append("BOT_TOKEN not set")
    
    if BOT_USERNAME == "your_bot_username":
        errors.append("BOT_USERNAME not set")
    
    # Check admin user IDs
    for user_id in ADMIN_USER_IDS:
        result = validate_user_id(str(user_id))
        if not result['valid']:
            errors.append(f"Invalid admin user ID: {user_id}")
    
    # Check paths
    if not os.path.exists(AGENTRYLAB_PATH):
        errors.append(f"AgentryLab path not found: {AGENTRYLAB_PATH}")
    
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("Configuration is valid")
        return True

if __name__ == "__main__":
    sys.exit(0 if validate_config() else 1)
```

#### **Run Validation**
```bash
python scripts/validate_config.py
```

### **2. Environment-Specific Configs**

#### **Development Config**
```python
# config/dev.py
from config import *

# Override for development
LOG_LEVEL = "DEBUG"
USE_REDIS = False
POLLING = True
```

#### **Staging Config**
```python
# config/staging.py
from config import *

# Override for staging
LOG_LEVEL = "INFO"
USE_REDIS = True
POLLING = False
WEBHOOK_URL = "https://staging.your-domain.com/webhook"
```

#### **Production Config**
```python
# config/prod.py
from config import *

# Override for production
LOG_LEVEL = "WARNING"
USE_REDIS = True
POLLING = False
WEBHOOK_URL = "https://your-domain.com/webhook"
```

---

## 📊 **Monitoring & Logging**

### **1. Logging Configuration**

#### **Structured Logging**
```python
# bot/utils/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'conversation_id'):
            log_entry['conversation_id'] = record.conversation_id
        
        return json.dumps(log_entry)

def setup_logging():
    """Set up structured logging."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler('/var/log/agentrybot/bot.log')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(console_handler)
```

### **2. Health Monitoring**

#### **Health Check Script**
```python
# scripts/health_check.py
import requests
import sys
import subprocess

def check_bot_health():
    """Check bot health status."""
    checks = []
    
    # Check systemd service
    try:
        result = subprocess.run(['systemctl', 'is-active', 'agentrybot'], 
                              capture_output=True, text=True)
        checks.append(('Service Status', result.stdout.strip() == 'active'))
    except Exception as e:
        checks.append(('Service Status', False))
    
    # Check webhook endpoint
    try:
        response = requests.get('https://your-domain.com/health', timeout=5)
        checks.append(('Webhook Health', response.status_code == 200))
    except Exception as e:
        checks.append(('Webhook Health', False))
    
    # Check Redis connection
    try:
        import redis
        r = redis.Redis.from_url('redis://localhost:6379/0')
        r.ping()
        checks.append(('Redis Connection', True))
    except Exception as e:
        checks.append(('Redis Connection', False))
    
    # Check log file
    try:
        with open('/var/log/agentrybot/bot.log', 'r') as f:
            f.seek(0, 2)  # Seek to end
            checks.append(('Log File', True))
    except Exception as e:
        checks.append(('Log File', False))
    
    # Report results
    all_healthy = True
    for check_name, status in checks:
        status_str = "✅" if status else "❌"
        print(f"{status_str} {check_name}")
        if not status:
            all_healthy = False
    
    return all_healthy

if __name__ == "__main__":
    sys.exit(0 if check_bot_health() else 1)
```

### **3. Metrics Collection**

#### **Prometheus Metrics**
```python
# bot/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
messages_total = Counter('bot_messages_total', 'Total messages processed', ['type'])
conversations_active = Gauge('bot_conversations_active', 'Active conversations')
response_time = Histogram('bot_response_time_seconds', 'Response time')
errors_total = Counter('bot_errors_total', 'Total errors', ['error_type'])

def start_metrics_server(port=8000):
    """Start Prometheus metrics server."""
    start_http_server(port)
```

#### **Grafana Dashboard**
```json
{
  "dashboard": {
    "title": "AgentryLab Bot Metrics",
    "panels": [
      {
        "title": "Active Conversations",
        "type": "stat",
        "targets": [
          {
            "expr": "bot_conversations_active"
          }
        ]
      },
      {
        "title": "Message Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(bot_messages_total[5m])"
          }
        ]
      }
    ]
  }
}
```

---

## 📈 **Scaling & Performance**

### **1. Horizontal Scaling**

#### **Load Balancer Configuration**
```nginx
# /etc/nginx/sites-available/agentrybot-cluster
upstream agentrybot_backend {
    server 127.0.0.1:8443;
    server 127.0.0.1:8444;
    server 127.0.0.1:8445;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    location /webhook {
        proxy_pass http://agentrybot_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### **Multiple Bot Instances**
```bash
# Start multiple instances
systemctl start agentrybot@1
systemctl start agentrybot@2
systemctl start agentrybot@3
```

### **2. Performance Optimization**

#### **Connection Pooling**
```python
# bot/utils/connection_pool.py
import asyncio
from agentrylab.telegram import TelegramAdapter

class AdapterPool:
    def __init__(self, pool_size=10):
        self.pool_size = pool_size
        self.adapters = []
        self.available = asyncio.Queue()
        
    async def initialize(self):
        """Initialize adapter pool."""
        for _ in range(self.pool_size):
            adapter = TelegramAdapter()
            await self.available.put(adapter)
    
    async def get_adapter(self):
        """Get adapter from pool."""
        return await self.available.get()
    
    async def return_adapter(self, adapter):
        """Return adapter to pool."""
        await self.available.put(adapter)
```

#### **Caching Strategy**
```python
# bot/utils/cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis.from_url('redis://localhost:6379/0')

def cache_result(expiry=300):
    """Cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, expiry, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

---

## 🔒 **Security Hardening**

### **1. System Security**

#### **Firewall Configuration**
```bash
# UFW configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### **Fail2Ban Setup**
```bash
# Install fail2ban
sudo apt install -y fail2ban

# Configure fail2ban
sudo nano /etc/fail2ban/jail.local
```

```ini
# /etc/fail2ban/jail.local
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
```

### **2. Application Security**

#### **Input Sanitization**
```python
# bot/utils/security.py
import re
import html

def sanitize_input(text):
    """Sanitize user input."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escape HTML entities
    text = html.escape(text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()
```

#### **Rate Limiting**
```python
# bot/utils/rate_limit.py
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id):
        """Check if user is within rate limits."""
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests
        user_requests[:] = [req_time for req_time in user_requests 
                           if now - req_time < self.time_window]
        
        # Check if under limit
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        
        return False
```

---

## 💾 **Backup & Recovery**

### **1. Backup Strategy**

#### **Automated Backup Script**
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/opt/backups/agentrybot"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="agentrybot_backup_$DATE.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application
tar -czf $BACKUP_DIR/$BACKUP_FILE \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    /home/agentrybot/agentrylab-telegram-bot

# Backup Redis data
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/log/agentrybot

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

#### **Cron Job Setup**
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/scripts/backup.sh
```

### **2. Recovery Procedures**

#### **Application Recovery**
```bash
# Stop service
sudo systemctl stop agentrybot

# Restore from backup
cd /home/agentrybot
tar -xzf /opt/backups/agentrybot/agentrybot_backup_YYYYMMDD_HHMMSS.tar.gz

# Restore dependencies
cd agentrylab-telegram-bot
source venv/bin/activate
pip install -r requirements.txt

# Start service
sudo systemctl start agentrybot
```

#### **Redis Recovery**
```bash
# Stop Redis
sudo systemctl stop redis-server

# Restore Redis data
sudo cp /opt/backups/agentrybot/redis_YYYYMMDD_HHMMSS.rdb /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb

# Start Redis
sudo systemctl start redis-server
```

---

## 🔧 **Maintenance Procedures**

### **1. Regular Maintenance**

#### **Weekly Tasks**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Check service status
sudo systemctl status agentrybot

# Review logs
sudo journalctl -u agentrybot --since "1 week ago"

# Check disk space
df -h

# Clean old logs
sudo find /var/log/agentrybot -name "*.log" -mtime +30 -delete
```

#### **Monthly Tasks**
```bash
# Update application dependencies
cd /home/agentrybot/agentrylab-telegram-bot
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart service
sudo systemctl restart agentrybot

# Review performance metrics
# Check Grafana dashboard

# Update SSL certificates
sudo certbot renew
```

### **2. Update Procedures**

#### **Application Updates**
```bash
# Create backup
/opt/scripts/backup.sh

# Stop service
sudo systemctl stop agentrybot

# Update code
cd /home/agentrybot/agentrylab-telegram-bot
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python run_tests.py

# Start service
sudo systemctl start agentrybot

# Verify functionality
sudo systemctl status agentrybot
```

---

## 🚨 **Troubleshooting**

### **1. Common Issues**

#### **Service Won't Start**
```bash
# Check service status
sudo systemctl status agentrybot

# Check logs
sudo journalctl -u agentrybot -f

# Check configuration
python scripts/validate_config.py

# Check dependencies
source venv/bin/activate
pip list
```

#### **Webhook Issues**
```bash
# Check nginx status
sudo systemctl status nginx

# Check nginx configuration
sudo nginx -t

# Check SSL certificates
sudo certbot certificates

# Test webhook endpoint
curl -X POST https://your-domain.com/webhook
```

#### **Redis Connection Issues**
```bash
# Check Redis status
sudo systemctl status redis-server

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log

# Test Redis connection
redis-cli ping
```

### **2. Performance Issues**

#### **High Memory Usage**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Check bot memory usage
ps aux | grep python

# Restart service if needed
sudo systemctl restart agentrybot
```

#### **Slow Response Times**
```bash
# Check system load
uptime
top

# Check network connectivity
ping telegram.org

# Check AgentryLab connection
curl -I http://localhost:8000  # Adjust port as needed
```

### **3. Emergency Procedures**

#### **Service Recovery**
```bash
# Emergency restart
sudo systemctl restart agentrybot

# If service fails to start
sudo systemctl stop agentrybot
sudo systemctl start agentrybot

# Check for errors
sudo journalctl -u agentrybot --since "5 minutes ago"
```

#### **Data Recovery**
```bash
# Restore from latest backup
/opt/scripts/restore.sh

# If Redis data is corrupted
sudo systemctl stop redis-server
sudo rm /var/lib/redis/dump.rdb
sudo systemctl start redis-server
```

---

## 📞 **Support Contacts**

### **Internal Support**
- **System Administrator**: admin@your-domain.com
- **Development Team**: dev@your-domain.com
- **Emergency Contact**: +1-XXX-XXX-XXXX

### **External Support**
- **Telegram Bot API**: @BotSupport
- **AgentryLab Support**: support@agentrylab.com
- **Server Provider**: Your hosting provider support

### **Documentation**
- **User Guide**: README.md
- **Technical Docs**: TECHNICAL_DOCUMENTATION.md
- **API Reference**: GitHub Wiki
- **Issue Tracker**: GitHub Issues

---

**This deployment guide provides comprehensive instructions for deploying, operating, and maintaining the AgentryLab Telegram Bot in production environments. For additional support, refer to the technical documentation and community resources.**

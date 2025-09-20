#!/bin/bash

# AgentryLab Telegram Bot Installation Script

set -e

echo "🤖 Installing AgentryLab Telegram Bot..."

# Check if Python 3.8+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install AgentryLab (from parent directory)
echo "🔧 Installing AgentryLab..."
if [ -d "../agentrylab" ]; then
    pip install -e ../agentrylab
    echo "✅ AgentryLab installed from local source"
else
    echo "❌ AgentryLab directory not found. Please ensure it's in the parent directory."
    exit 1
fi

# Install bot dependencies
echo "📦 Installing bot dependencies..."
pip install -r requirements.txt

# Create config file if it doesn't exist
if [ ! -f "config.py" ]; then
    echo "⚙️ Creating config.py from template..."
    cp config.example.py config.py
    echo "✅ Config file created. Please edit config.py with your bot token."
else
    echo "✅ Config file already exists"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.py with your bot token from @BotFather"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python bot/main.py"
echo ""
echo "For help, see README.md"

#!/bin/bash
# 🚀 Super Simple Deployment Script for AgentryLab Telegram Bot

set -e

echo "🚀 Starting AgentryLab Telegram Bot Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    print_status "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    print_status "Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from example..."
    if [ -f env.example ]; then
        cp env.example .env
        print_warning "Please edit .env file with your configuration before running again."
        print_status "Required: BOT_TOKEN, BOT_USERNAME, AGENTRYLAB_PATH"
        exit 1
    else
        print_error "env.example file not found. Cannot create .env file."
        exit 1
    fi
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs data ssl

# Set proper permissions
chmod 755 logs data ssl

# Check if AgentryLab path exists
AGENTRYLAB_PATH=$(grep AGENTRYLAB_PATH .env | cut -d '=' -f2)
if [ ! -d "$AGENTRYLAB_PATH" ]; then
    print_warning "AgentryLab path '$AGENTRYLAB_PATH' does not exist."
    print_status "Please update AGENTRYLAB_PATH in .env file to point to your AgentryLab installation."
    exit 1
fi

# Build and start the bot
print_status "Building Docker image..."
docker-compose build

print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 10

# Check if bot is running
if docker-compose ps | grep -q "agentrybot.*Up"; then
    print_success "AgentryLab Telegram Bot is running!"
    print_status "Check logs with: docker-compose logs -f agentrybot"
    print_status "Stop bot with: docker-compose down"
    print_status "Update bot with: docker-compose pull && docker-compose up -d"
else
    print_error "Bot failed to start. Check logs with: docker-compose logs agentrybot"
    exit 1
fi

# Show status
print_status "Service Status:"
docker-compose ps

print_success "Deployment completed successfully! 🎉"

#!/bin/bash
# Deployment and startup helper script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AI Scientific Co-Investigator - Deployment Script${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please update .env with your API keys${NC}"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose available${NC}"

# Parse arguments
case "${1:-}" in
    "build")
        echo -e "${GREEN}🔨 Building Docker images...${NC}"
        docker compose build
        ;;
    "up")
        echo -e "${GREEN}🚀 Starting services...${NC}"
        docker compose up -d
        sleep 5
        echo -e "${GREEN}✓ Services started${NC}"
        echo -e "${GREEN}📍 API: http://localhost:8000${NC}"
        echo -e "${GREEN}📍 Docs: http://localhost:8000/docs${NC}"
        echo -e "${GREEN}📍 Qdrant: http://localhost:6333${NC}"
        docker compose logs -f api
        ;;
    "down")
        echo -e "${YELLOW}⬇️  Stopping services...${NC}"
        docker compose down
        ;;
    "logs")
        docker compose logs -f api
        ;;
    "test")
        echo -e "${GREEN}🧪 Running tests...${NC}"
        docker compose exec api pytest app/tests/ -v
        ;;
    "migrate")
        echo -e "${GREEN}🔄 Running database migrations...${NC}"
        docker compose exec api alembic upgrade head
        ;;
    "shell")
        echo -e "${GREEN}💻 Opening Python shell...${NC}"
        docker compose exec api python
        ;;
    "dev")
        echo -e "${GREEN}🛠️  Development mode - rebuilding and starting...${NC}"
        docker compose down
        docker compose build
        docker compose up
        ;;
    *)
        echo -e "${YELLOW}Usage:${NC}"
        echo "  $0 build       - Build Docker images"
        echo "  $0 up          - Start all services"
        echo "  $0 down        - Stop all services"
        echo "  $0 logs        - View API logs"
        echo "  $0 test        - Run tests"
        echo "  $0 migrate     - Run database migrations"
        echo "  $0 shell       - Open Python shell"
        echo "  $0 dev         - Development mode"
        ;;
esac

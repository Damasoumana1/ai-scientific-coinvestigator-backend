#!/bin/bash
# HACKATHON EMERGENCY SETUP - Run this now!

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  K2 THINK HACKATHON - EMERGENCY SETUP ║${NC}"
echo -e "${BLUE}║        Deadline: March 10, 2026      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}⏱️  You have ~36 hours to submit!${NC}\n"

# Check Python
echo -e "${GREEN}[1/5] Checking Python environment...${NC}"
python --version
python -m venv --version 2>/dev/null || echo "venv module available"

# Create venv
echo -e "${GREEN}[2/5] Creating fresh Python environment...${NC}"
rm -rf .venv 2>/dev/null || true
python -m venv .venv
source .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate

# Install dependencies
echo -e "${GREEN}[3/5] Installing dependencies (this may take 2 minutes)...${NC}"
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Test imports
echo -e "${GREEN}[4/5] Testing imports...${NC}"
python -c "from fastapi import FastAPI; print('✓ FastAPI OK')"
python -c "from sqlalchemy import Column; print('✓ SQLAlchemy OK')"
python -c "from langgraph.graph import StateGraph; print('✓ LangGraph OK')"
python -c "import httpx; print('✓ httpx OK')"
python -c "from qdrant_client import QdrantClient; print('✓ Qdrant OK')"

# Run demo
echo -e "${GREEN}[5/5] Running demo...${NC}\n"
python HACKATHON_DEMO.py

echo -e "\n${GREEN}✅ SETUP COMPLETE!${NC}"
echo -e "${YELLOW}📹 Next: Run the demo again and record your screen${NC}"
echo -e "${YELLOW}📤 Then submit to: https://build.k2think.ai/demo-submission/${NC}\n"

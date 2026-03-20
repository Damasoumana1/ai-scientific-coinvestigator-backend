# Installation script for Python 3.13 compatibility
Write-Host "Step 1: Upgrade pip..." -ForegroundColor Green
python -m pip install --upgrade pip --quiet

Write-Host "Step 2: Install core dependencies..." -ForegroundColor Green
pip install `
  fastapi==0.104.1 `
  uvicorn==0.24.0 `
  pydantic==2.5.0 `
  pydantic-settings==2.1.0 `
  sqlalchemy==2.0.23 `
  psycopg2-binary==2.9.9 `
  python-multipart==0.0.6 `
  --quiet

Write-Host "Step 3: Install AI/LangGraph dependencies..." -ForegroundColor Green
pip install `
  langgraph==0.0.39 `
  langchain==0.1.0 `
  openai==1.3.0 `
  --quiet

Write-Host "Step 4: Install RAG/Vector dependencies..." -ForegroundColor Green
pip install `
  qdrant-client==2.4.0 `
  pypdf==3.17.1 `
  pymupdf==1.23.8 `
  unstructured==0.12.0 `
  --quiet

Write-Host "Step 5: Install infrastructure dependencies..." -ForegroundColor Green
pip install `
  redis==5.0.1 `
  celery==5.3.4 `
  httpx==0.25.2 `
  aiohttp==3.9.1 `
  --quiet

Write-Host "Step 6: Test imports..." -ForegroundColor Green
python -c "
import fastapi
import uvicorn
import pydantic
import sqlalchemy
import langgraph
print('✓ All core imports successful!')
"

Write-Host "Done! Ready to start." -ForegroundColor Green

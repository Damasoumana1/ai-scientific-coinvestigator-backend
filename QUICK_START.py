#!/usr/bin/env python3
"""
Quick Start Guide - Step-by-step instructions
"""

QUICK_START = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   AI Scientific Co-Investigator - QUICK START                ║
╚══════════════════════════════════════════════════════════════════════════════╝

🚀 OPTION 1: Docker Compose (Recommended - 5 minutes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Prerequisites:
   ✓ Install Docker: https://www.docker.com/products/docker-desktop
   ✓ Install Docker Compose (included with Docker Desktop)

2. Setup:
   $ cp .env.example .env
   $ # Edit .env - add your API keys
   
3. Start services:
   $ chmod +x deploy.sh
   $ ./deploy.sh up
   
   ✓ API: http://localhost:8000
   ✓ Docs: http://localhost:8000/docs
   ✓ Qdrant: http://localhost:6333
   ✓ PostgreSQL: localhost:5432

4. Verify health:
   $ curl http://localhost:8000/health/ready
   → Should return: {"ready": true, ...}

5. Stop:
   $ ./deploy.sh down


🛠️ OPTION 2: Local Python Development
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Prerequisites:
   ✓ Python 3.10+
   ✓ PostgreSQL 13+
   ✓ Redis
   ✓ Qdrant

2. Setup environment:
   $ python -m venv .venv
   $ source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
   
3. Install dependencies:
   $ pip install -r requirements.txt
   
4. Configure:
   $ cp .env.example .env
   $ # Edit .env with your local DB credentials
   
5. Start services (in separate terminals):
   Terminal 1 - PostgreSQL:
   $ psql -U user -d scoinvestigator
   
   Terminal 2 - Redis:
   $ redis-server
   
   Terminal 3 - Qdrant:
   $ docker run -p 6333:6333 qdrant/qdrant
   
   Terminal 4 - API:
   $ uvicorn app.main:app --reload
   → http://localhost:8000


📚 COMMON OPERATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Health Check:
  $ curl http://localhost:8000/health/ready
  
View API Docs:
  → Open browser: http://localhost:8000/docs

View Logs:
  $ ./deploy.sh logs
  
Run Tests:
  $ ./deploy.sh test
  
Database: psql connection
  $ psql -U user -d scoinvestigator -h localhost
  
Stop Everything:
  $ ./deploy.sh down


🚀 FIRST API CALL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run an analysis:
  
  $ curl -X POST http://localhost:8000/api/v1/analysis/run \\
    -H "Content-Type: application/json" \\
    -d '{
      "documents": ["Document text here..."],
      "analysis_type": "comprehensive"
    }'
  
View results:
  
  $ curl http://localhost:8000/api/v1/analysis/{analysis_id}/results


📊 DATABASE SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Create database (first time):
  
  $ psql -U postgres
  postgres=# CREATE DATABASE scoinvestigator;
  postgres=# CREATE USER user WITH PASSWORD 'onion123';
  postgres=# GRANT ALL PRIVILEGES ON DATABASE scoinvestigator TO user;
  
Tables are created automatically by SQLAlchemy on first run.


🔍 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem: Import errors
Solution: pip install --upgrade -r requirements.txt

Problem: Database connection failed
Solution: Check DATABASE_URL in .env
        Check PostgreSQL is running
        psql -U user -d scoinvestigator
        
Problem: Qdrant not responding
Solution: docker run -p 6333:6333 qdrant/qdrant
        curl http://localhost:6333/health
        
Problem: Ports already in use
Solution: Check what's using the port:
        lsof -i :8000  # for API
        lsof -i :5432  # for DB
        Kill the process: kill -9 <PID>
        Or change ports in docker-compose.yml


📖 STRUCTURE OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/app
  /api          → API routes
  /db           → Database models & sessions
  /services     → Business logic
  /reasoning    → AI orchestration (LangGraph)
  /rag          → Document processing
  /modules      → Analysis modules
  /core         → Configuration & utilities
  main.py       → FastAPI app


🎯 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Verify all services running:
   $ curl http://localhost:8000/health/ready
   
2. Try the API with sample data:
   → Visit http://localhost:8000/docs
   → Try POST /api/v1/analysis/run
   
3. Check logs for errors:
   $ ./deploy.sh logs
   
4. Monitor resources:
   $ docker stats
   
5. Setup frontend (separate project):
   → See FRONTEND_SCAFFOLD.md


📞 NEED HELP?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Read the docs:
   - README.md (project overview)
   - DEPLOYMENT.md (deployment guide)
   - STACK_ANALYSIS.md (tech stack details)
   - FRONTEND_SCAFFOLD.md (frontend setup)
   
2. Check logs:
   - Docker: docker-compose logs
   - API: ./deploy.sh logs
   - Database: psql logs
   
3. API Docs:
   - Swagger: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   
4. Health checks:
   - All services: http://localhost:8000/health/ready
   - API only: http://localhost:8000/health/


👨‍💻 DEVELOPMENT WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Edit code → Changes auto-reload (with --reload flag)
Run tests → ./deploy.sh test
View logs → ./deploy.sh logs
Debug   → Add print statements → Check logs


🎊 YOU'RE ALL SET!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next: Start making requests to the API!

Happy coding! 🚀
"""

if __name__ == "__main__":
    print(QUICK_START)
    
    # Additional interactive help
    import sys
    
    print(\"\\n\" + \"=\"*80)
    print(\"INTERACTIVE QUICK START\")
    print(\"=\"*80)
    
    choice = input(\"\\nHow do you want to run the app?\\n1. Docker Compose (recommended)\\n2. Local Python\\n> \").strip()
    
    if choice == '1':
        print(\"\\n\" + \"=\"*80)
        print(\"DOCKER COMPOSE SETUP\")
        print(\"=\"*80)
        print(\"\\nSteps:\")
        print(\"1. cp .env.example .env\")
        print(\"2. Edit .env with your API keys\")
        print(\"3. chmod +x deploy.sh\")
        print(\"4. ./deploy.sh up\")
        print(\"\\nThen visit: http://localhost:8000/docs\")
        
    elif choice == '2':
        print(\"\\n\" + \"=\"*80)
        print(\"LOCAL PYTHON SETUP\")
        print(\"=\"*80)
        print(\"\\nSteps:\")
        print(\"1. python -m venv .venv\")
        print(\"2. source .venv/bin/activate\")
        print(\"3. pip install -r requirements.txt\")
        print(\"4. Start PostgreSQL, Redis, Qdrant\")
        print(\"5. uvicorn app.main:app --reload\")
        print(\"\\nThen visit: http://localhost:8000/docs\")
    
    print(\"\\n\" + \"=\"*80)
    print(\"Questions? Check: README.md | DEPLOYMENT.md | STACK_ANALYSIS.md\")
    print(\"=\"*80 + \"\\n\")

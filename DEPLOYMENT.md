# Deployment Guide

## 🚀 Quick Start (Local Development)

### 1. Environment Setup
```bash
# Copy environment variables
cp .env.example .env

# Update .env with your keys
# - OPENAI_API_KEY
# - K2_THINK_API_KEY
# - DATABASE_URL (if not using Docker)
```

### 2. Docker Compose (Recommended)
```bash
# Start all services with live-reload enabled
docker compose up -d

# Services running:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Qdrant: http://localhost:6333
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

> [!TIP]
> **Live-Reloading**: The `docker-compose.yml` is configured to mount the `./app` directory into the container. Most backend code changes will be reflected immediately without restarting the container.

### 3. First Run
```bash
# Check health
curl http://localhost:8000/health/ready

# Run tests
./deploy.sh test

# View logs
./deploy.sh logs
```

---

## 🌐 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Analysis
```
POST /api/analysis/run
- Start comprehensive analysis
- Body: { documents: [...], analysis_type: "comprehensive" }

GET /api/analysis/{analysis_id}/status
- Check analysis status

GET /api/analysis/{analysis_id}/results
- Get analysis results
```

#### Health
```
GET /health/
- Basic health check

GET /health/ready
- Full readiness check with all dependencies

GET /health/live
- Liveness probe (Kubernetes ready)
```

---

## 🐳 Docker Commands

### Development
```bash
# Start in development mode (with reload)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild images
docker-compose build

# Remove volumes (WARNING: data loss)
docker-compose down -v
```

### Production

#### Option 1: Railway.app (Recommended for Hackathon)

1. **Create Railway account**: https://railway.app

2. **Deploy from Git**:
   ```bash
   # Railway will auto-detect docker-compose.yml
   # Services automatically created:
   # - PostgreSQL
   # - Redis
   # - FastAPI API
   # - Celery Worker
   ```

3. **Environment variables**:
   - Set in Railway dashboard
   - Same as .env file

4. **DNS & Domains**:
   - Railway provides automatic domain
   - Custom domain via dashboard

#### Option 2: AWS ECS/Kubernetes

```bash
# Build and push to ECR
aws ecr create-repository --repository-name scoinvestigator-api

docker build -t scoinvestigator-api .
docker tag scoinvestigator-api:latest <aws-account>.dkr.ecr.us-east-1.amazonaws.com/scoinvestigator-api:latest
docker push <aws-account>.dkr.ecr.us-east-1.amazonaws.com/scoinvestigator-api:latest

# Deploy via ECS/CloudFormation
# OR push to ECR and use AWS Console
```

#### Option 3: Vercel (Frontend) + Render (Backend)

```bash
# Backend on Render
# 1. Push repo to GitHub
# 2. Connect to Render.com
# 3. Select docker-compose.yml
# 4. Deploy

# Frontend on Vercel
# 1. Create Next.js project
# 2. Connect GitHub
# 3. Set API_URL env var
# 4. Deploy
```

---

## 🔧 Configuration

### Database Migrations (Alembic)

```bash
# Create new migration
docker-compose exec api alembic revision --autogenerate -m "Add new table"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback
docker-compose exec api alembic downgrade -1
```

### Celery Tasks

```bash
# Monitor Celery
docker-compose exec api celery -A app.workers.tasks inspect active

# Purge queue
docker-compose exec api celery -A app.workers.tasks purge
```

---

## 🧪 Testing

### Run Tests
```bash
# All tests
./deploy.sh test

# Specific test file
docker-compose exec api pytest app/tests/test_analysis.py -v

# With coverage
docker-compose exec api pytest --cov=app --cov-report=html
```

### Test Coverage Report
```bash
# Generate and view
docker-compose exec api pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 📊 Monitoring

### Health Checks

The system includes built-in health checks for orchestration:

- **API**: `GET /health/` (trailing slash required)
- **PostgreSQL**: `pg_isready -d scoinvestigator`
- **Frontend**: Check on port 3000

```bash
# Check API health
curl -I http://localhost:8000/health/
```

### Logs

```bash
# FastAPI logs
./deploy.sh logs

# Celery logs
docker-compose logs -f celery_worker

# PostgreSQL logs
docker-compose logs -f postgres

# All services
docker-compose logs -f
```

### Performance Monitoring

```bash
# Resource usage
docker stats

# Database connections
docker-compose exec postgres psql -U user -d scoinvestigator -c "SELECT count(*) FROM pg_stat_activity;"

# Redis memory
docker-compose exec redis redis-cli INFO memory
```

---

## 🔒 Security Checklist

### Before Production Deployment

- [ ] Update SECRET_KEY in .env (use `os.urandom(32)`)
- [ ] Set strong DB password
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable API rate limiting
- [ ] Configure log retention
- [ ] Set up backups for PostgreSQL
- [ ] Use environment variables (never commit secrets)
- [ ] Enable authentication on all endpoints
- [ ] Set up monitoring/alerting
- [ ] Review and test error handling

---

## 📈 Scaling

### Horizontal Scaling (Long-term)

```yaml
# With Kubernetes
# 1. Multiple API replicas
# 2. PostgreSQL cluster (or managed RDS)
# 3. Qdrant cluster
# 4. Redis cluster
# 5. Load balancer (ingress)
```

```yaml
# With Docker Swarm
docker swarm init
docker stack deploy -c docker-compose.yml scoinvestigator
```

### Vertical Scaling

```yaml
# Increase resources in docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## 🐛 Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Check ports are available
lsof -i :8000  # API
lsof -i :5432  # PostgreSQL
lsof -i :6333  # Qdrant
lsof -i :6379  # Redis

# Restart everything
docker-compose down -v
docker-compose up
```

### Database connection errors

```bash
# Verify database is running
docker-compose exec postgres psql -U user -c "SELECT 1"

# Check connection string in .env
DATABASE_URL=postgresql://user:onion123@postgres:5432/scoinvestigator
```

### Qdrant not responding

```bash
# Check Qdrant health
curl http://localhost:6333/health

# Restart Qdrant
docker-compose restart qdrant
```

### API crashes

```bash
# View error logs
docker-compose logs api --tail=100

# Rebuild and restart
docker-compose build api
docker-compose up api
```

---

## 📞 Support

For issues:
1. Check logs: `./deploy.sh logs`
2. Verify health: `curl http://localhost:8000/health/ready`
3. Check Docker: `docker-compose ps`
4. Review documentation in `/docs` endpoint
5. Open GitHub issue with logs

---

## 🎯 Next Steps

1. **Local Testing**: Run locally with Docker Compose
2. **Frontend Integration**: Setup Next.js frontend
3. **Production Deployment**: Deploy to Railway or AWS
4. **Monitoring Setup**: Configure observability stack
5. **Auto-scaling**: Setup scaling policies for load

Happy deploying! 🚀

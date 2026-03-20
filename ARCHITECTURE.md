# Architecture & System Design

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                   │
│                                                                              │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐   │
│  │   Next.js Web   │  │  React Flow UI   │  │   Visualization Layer    │   │
│  │  (Frontend)     │  │  (Graph Browser) │  │   D3.js, Cytoscape       │   │
│  └────────┬────────┘  └────────┬─────────┘  └────────────┬────────────┘   │
│           │                    │                         │                  │
│           └────────────────────┼─────────────────────────┘                  │
│                                │ HTTPS/REST                                 │
│                                ↓                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY LAYER                               │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         FastAPI Router                               │  │
│  │  GET/POST /api/v1/analysis/run                                       │  │
│  │  GET      /api/v1/analysis/{id}/results                              │  │
│  │  POST     /api/v1/papers/upload                                      │  │
│  │  GET      /api/v1/health/ready                                       │  │
│  │  [+ 20+ more endpoints]                                              │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                ↓                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATION LAYER                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    LangGraph State Machine                           │  │
│  │                                                                      │  │
│  │   [Input] → [Extract] → [Contradictions] → [Hypotheses]            │  │
│  │                ↓           ↓               ↓                        │  │
│  │           [Gaps] → [Protocols (3x)] → [Self-Critique]              │  │
│  │                          ↓                                          │  │
│  │                      [Output]                                       │  │
│  │                                                                      │  │
│  │  • Multi-step reasoning workflow                                    │  │
│  │  • Self-consistency layer (3 versions → best selection)             │  │
│  │  • Fallback to LLM if K2 unavailable                                │  │
│  │  • Audit trail of every step                                        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                ↓                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            SERVICES LAYER                                   │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Analysis    │  │  Paper       │  │  Project     │  │  Protocol    │  │
│  │  Service     │  │  Service     │  │  Service     │  │  Service     │  │
│  │              │  │              │  │              │  │              │  │
│  │  • Run       │  │  • Upload    │  │  • Create    │  │  • Generate  │  │
│  │  • Track     │  │  • Parse     │  │  • Manage    │  │  • Validate  │  │
│  │  • Results   │  │  • Chunk     │  │  • Query     │  │  • Export    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          PROCESSING LAYER                                   │
│                                                                              │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  PDF Parser     │  │  Embeddings      │  │  K2 Think Client │          │
│  │                 │  │  Generator       │  │                  │          │
│  │  • PyMuPDF      │  │                  │  │  • Analyze       │          │
│  │  • PyPDF2       │  │  • OpenAI API    │  │  • Generate      │          │
│  │  • Unstructured │  │  • Fallback LLM  │  │  • Critique      │          │
│  │                 │  │                  │  │                  │          │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬─────────┘          │
│           │                    │                     │                     │
│           └────────────────────┼─────────────────────┘                     │
│                                ↓                                           │
│            ┌──────────────────────────────────────────┐                   │
│            │     Vector Store & Semantic Search      │                   │
│            │          (Qdrant Integration)           │                   │
│            └──────────────────────────────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA PERSISTENCE LAYER                             │
│                                                                              │
│  ┌─────────────────────────┐  ┌─────────────────────────────────────────┐ │
│  │   PostgreSQL (Primary)  │  │   Qdrant (Vector DB)                    │ │
│  │                         │  │                                         │ │
│  │  ├─ users              │  │  ├─ paper_embeddings                     │ │
│  │  ├─ projects           │  │  ├─ chunk_embeddings                     │ │
│  │  ├─ research_papers    │  │  └─ semantic_search_index                │ │
│  │  ├─ paper_chunks       │  │                                         │ │
│  │  ├─ analysis_runs      │  │  + Hybrid search (keyword + semantic)    │ │
│  │  ├─ contradictions     │  │                                         │ │
│  │  ├─ hypotheses         │  │                                         │ │
│  │  ├─ protocols          │  │                                         │ │
│  │  ├─ reasoning_traces   │  │                                         │ │
│  │  ├─ activity_logs      │  │                                         │ │
│  │  └─ research_gaps      │  │                                         │ │
│  │                         │  │                                         │ │
│  │  UUID Primary Keys      │  │  Persistent Collections                │ │
│  │  JSONB for flexibility  │  │  Fast similarity search                 │ │
│  │  Audit trail support    │  │  Metadata filtering                     │ │
│  │                         │  │                                         │ │
│  └─────────────────────────┘  └─────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURE LAYER                                │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Docker     │  │   Redis      │  │   PostgreSQL │  │   Qdrant     │  │
│  │  Containers  │  │   (Cache)    │  │   (Primary   │  │   (Vector    │  │
│  │              │  │              │  │   Data)      │  │   Search)    │  │
│  │  • API       │  │  • Queue     │  │              │  │              │  │
│  │  • Workers   │  │  • Cache     │  │  • Cluster   │  │  • Cluster   │  │
│  │  • Compose   │  │  • Sessions  │  │  • Backup    │  │  • Replicas  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │              Deployment Orchestration                             │   │
│  │  • Railway (Hackathon - simple)                                   │   │
│  │  • Kubernetes (Startup - scalable)                                │   │
│  │  • AWS ECS / GCP Cloud Run (Enterprise)                           │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

```
1. USER UPLOADS PAPERS
   ↓
   User → [Frontend Upload] → FastAPI /papers/upload → Storage

2. SYSTEM PROCESSES WITH ORCHESTRATION
   ↓
   Papers → [PDFParser] → [Chunking] → [Embeddings]
                ↓              ↓            ↓
   Content  ←──┴──────────────┴────────────┴→ [Qdrant Vector DB]

3. ANALYSIS WORKFLOW (LangGraph)
   ↓
   [Extract] → [Contradictions] → [Hypotheses] → [Gaps]
      ↓             ↓               ↓           ↓
   Use: K2 API + OpenAI LLM for each step
   
4. PROTOCOL GENERATION WITH SELF-CRITIQUE
   ↓
   [Generate v1] ─┐
   [Generate v2] ─┼→ [Select Best] → [Validate] → [Store]
   [Generate v3] ─┘
   
5. RESULTS STORED & QUERYABLE
   ↓
   PostgreSQL ← [Analysis Results]
   PostgreSQL ← [Contradictions]
   PostgreSQL ← [Protocols]
   PostgreSQL ← [Audit Trail]

6. FRONTEND VISUALIZES
   ↓
   Results → [API] → [React Components] → [User Views]
              ↓
   Reasoning Trace → [React Flow Graph]
   Contradictions → [Data Table + Severity]
   Protocols → [Rich Editor + Export]
```

---

## 📊 Technology Stack Layers

```
┌──────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  Next.js | React 18 | Tailwind CSS | React Flow | D3.js      │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                    API LAYER                                 │
│  FastAPI | Uvicorn | Pydantic | OpenAPI (Swagger)           │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                         │
│  LangGraph | LangChain | K2 Think API | OpenAI GPT-4        │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                   PROCESSING LAYER                           │
│  PyMuPDF | Unstructured | sentence-transformers | Qdrant     │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  PostgreSQL | SQLAlchemy | Qdrant | Redis                    │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│                INFRASTRUCTURE LAYER                          │
│  Docker | Docker Compose | Kubernetes/Railway/AWS            │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Architecture

### Development (Local)
```
┌─────────────────────────────────────┐
│     Docker Compose on Localhost     │
├─────────────────────────────────────┤
│  Frontend (Next.js)   :3000        │
│  API (FastAPI)        :8000        │
│  PostgreSQL           :5432        │
│  Qdrant               :6333        │
│  Redis                :6379        │
└─────────────────────────────────────┘
```

### Hackathon (Railway)
```
┌─────────────────────────────────────┐
│          Railway.app                │
├─────────────────────────────────────┤
│  API Service                        │
│  ├─ Auto-scaling                    │
│  ├─ Load balancing                  │
│  └─ HTTPS + domain                  │
│                                     │
│  PostgreSQL (Managed)               │
│  Redis (Managed)                    │
│  Environment variables              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│          Vercel.app                 │
├─────────────────────────────────────┤
│  Next.js Frontend                   │
│  ├─ Edge functions                  │
│  ├─ CDN                             │
│  └─ Analytics                       │
└─────────────────────────────────────┘
```

### Production (AWS)
```
┌──────────────────────────────────────────────────────────┐
│                    AWS Region                           │
├──────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────┐         │
│  │  API Tier                                  │         │
│  │  ├─ Application Load Balancer (ALB)       │         │
│  │  ├─ ECS Fargate (Auto-scaling)            │         │
│  │  ├─ CloudWatch Logs                       │         │
│  │  └─ EC2 Auto Scaling Groups               │         │
│  └─────────────────────────────────────────────┘         │
│                     ↓                                    │
│  ┌─────────────────────────────────────────────┐         │
│  │  Data Tier                                 │         │
│  │  ├─ RDS PostgreSQL (Multi-AZ)             │         │
│  │  ├─ ElastiCache Redis                      │         │
│  │  ├─ S3 for PDF storage                    │         │
│  │  └─ Secrets Manager                       │         │
│  └─────────────────────────────────────────────┘         │
│                     ↓                                    │
│  ┌─────────────────────────────────────────────┐         │
│  │  Vector Search Tier                        │         │
│  │  ├─ Qdrant cluster (3-5 nodes)            │         │
│  │  ├─ OpenSearch Domain (optional)           │         │
│  │  └─ CloudFront distribution                │         │
│  └─────────────────────────────────────────────┘         │
│                     ↓                                    │
│  ┌─────────────────────────────────────────────┐         │
│  │  Frontend Tier                             │         │
│  │  ├─ CloudFront CDN                         │         │
│  │  ├─ Route 53 DNS                           │         │
│  │  └─ Certificate Manager SSL/TLS            │         │
│  └─────────────────────────────────────────────┘         │
│                     ↓                                    │
│  ┌─────────────────────────────────────────────┐         │
│  │  Monitoring & Analytics                    │         │
│  │  ├─ CloudWatch                             │         │
│  │  ├─ X-Ray tracing                          │         │
│  │  ├─ GuardDuty (security)                   │         │
│  │  └─ Cost Explorer                          │         │
│  └─────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  SECURITY LAYERS                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─ Network Level ─────────────────────────────────┐   │
│  │ • VPC isolation (AWS)                           │   │
│  │ • Security groups (firewall rules)              │   │
│  │ • WAF (Web Application Firewall)                │   │
│  │ • DDoS protection (CloudFlare/AWS Shield)       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─ Transport Level ───────────────────────────────┐   │
│  │ • HTTPS/TLS 1.3                                │   │
│  │ • Certificate pinning                          │   │
│  │ • Encryption in transit                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─ Application Level ─────────────────────────────┐   │
│  │ • API authentication (JWT tokens)              │   │
│  │ • Rate limiting                                │   │
│  │ • Input validation & sanitization              │   │
│  │ • CORS configuration                           │   │
│  │ • Security headers (CSP, HSTS)                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─ Data Level ────────────────────────────────────┐   │
│  │ • Database encryption at rest                  │   │
│  │ • Password hashing (bcrypt)                    │   │
│  │ • Secrets management (AWS Secrets Manager)     │   │
│  │ • PII masking in logs                          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─ Audit & Compliance ────────────────────────────┐   │
│  │ • Activity logging (all operations)            │   │
│  │ • Audit trail immutability                     │   │
│  │ • Data retention policies                      │   │
│  │ • Compliance monitoring (GDPR, HIPAA)          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📈 Scalability Path

```
Phase 1: MVP (Hackathon)
├─ Docker Compose locally
├─ Single API server
├─ PostgreSQL single instance
├─ Qdrant single node
└─ Manual scaling

         ↓

Phase 2: Early Startup
├─ Railway deployment
├─ Managed database
├─ Redis cluster
├─ Qdrant cluster (3 nodes)
├─ Auto-scaling enabled
└─ ~1k users

         ↓

Phase 3: Growth
├─ AWS multi-region
├─ RDS Multi-AZ
├─ Load balancing
├─ Caching strategy
├─ Async processing
└─ ~10k users

         ↓

Phase 4: Enterprise
├─ Kubernetes cluster
├─ Database sharding
├─ Vector DB cluster
├─ Multiple regions
├─ Advanced monitoring
└─ ~100k+ users
```

---

## 🎯 Summary

| Component | Technology | Role |
|-----------|-----------|------|
| **Frontend** | Next.js, React, Tailwind | User interface |
| **API** | FastAPI, Uvicorn | REST endpoints |
| **Orchestration** | LangGraph, LangChain | Multi-step workflows |
| **AI** | K2 Think V2, OpenAI GPT-4 | Deep reasoning |
| **Document Processing** | PyMuPDF, Unstructured | PDF extraction |
| **Embeddings** | OpenAI embeddings | Vector generation |
| **Vector Search** | Qdrant | Semantic search |
| **Primary DB** | PostgreSQL | Structured data |
| **Cache** | Redis | Performance |
| **Deployment** | Docker, Railway/AWS | Infrastructure |

---

**This architecture is hackathon-ready AND scalable to production!** 🚀

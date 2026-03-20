---
title: AI Scientific Co-Investigator Backend
emoji: 🧪
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# AI Scientific Co-Investigator Backend

This is the FastAPI backend for the AI Scientific Co-Investigator platform, deployed on Hugging Face Spaces.

## Prerequisites

- **Supabase**: Relational Database (PostgreSQL)
- **Qdrant Cloud**: Vector Database
- **Upstash**: Redis Cache/Broker (for Celery)

## Deployment

To deploy this to your Hugging Face Space:

1. Clone your Space repository.
2. Copy all files from this backend repository to the Space repository.
3. Push the changes.

## Environment Variables (Secrets)

Make sure to set the following secrets in your Hugging Face Space settings:

- `DATABASE_URL`: Your Supabase connection string.
- `SECRET_KEY`: A secure random string for JWT.
- `OPENAI_API_KEY`: Your OpenAI API key.
- `ALLOWED_ORIGINS`: Comma-separated list of origins (e.g., `https://your-frontend.vercel.app`).
- `QDRANT_URL`: Your Qdrant Cloud URL.
- `QDRANT_API_KEY`: Your Qdrant Cloud API key.
- `CELERY_BROKER_URL`: Your Upstash Redis URL.
- `CELERY_RESULT_BACKEND`: Your Upstash Redis URL.

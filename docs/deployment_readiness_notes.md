# PatentIQ Production Deployment Readiness Notes (Phase 5)

This document outlines system prerequisites, environment configurations, and startup guidelines to transition PatentIQ into staging and production hosting.

## 1. System Requirements
- **Python:** Version 3.10 or higher.
- **RAM:** Minimum 8 GB (16 GB recommended to support local SentenceTransformer model execution and ChromaDB index caching).
- **GPU (Optional):** CUDA-compatible GPU to accelerate query embedding generations (SentenceTransformers auto-detects CUDA availability).

## 2. Environment Configurations (`.env`)
Create a `.env` file in the root directory containing:
```ini
# Google Gemini API Credentials
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here

# LLM Engine Configuration
GEMINI_MODEL=gemini-2.5-flash

# Mock Engine Mode (set to 'false' in production to run live Gemini API calls)
MOCK_LLM=false
```

## 3. Installation Steps
Install all runtime dependencies:
```bash
pip install -r requirements.txt
```

## 4. Startup Commands (Development / Local Run)
To start the FastAPI server with auto-reloading:
```bash
uvicorn backend.api.main:app --reload --port 8000
```
Then navigate to: `http://127.0.0.1:8000`

## 5. Staging/Production Deployment Guidelines

### Application Servers
In staging or production environments, run Uvicorn with multiple workers behind a reverse proxy (e.g. Nginx).
```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Static Files Optimization
For high-traffic production deployments, configure Nginx to serve the `frontend/` directory statically directly from the filesystem, bypassing Python/Uvicorn runtime overhead for asset delivery.

Nginx configuration example snippet:
```nginx
server {
    listen 80;
    server_name patentiq.example.com;

    # Static Frontend
    location / {
        root /path/to/PatentIQ/frontend;
        try_files $uri $uri/ /index.html;
    }

    # Proxy to FastAPI backend
    location /api {
        proxy_pass http://127.0.0.1:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Rate Limiting & Gemini Quotas
The Gemini Free Tier allows 5 RPM (Requests Per Minute).
- Our backend includes a custom rate-limiting lock of 12.5 seconds between model calls.
- In multi-worker production deployments, configure redis-based rate limiting to prevent hitting Gemini quota thresholds across multiple worker processes.
- Upgrade to the Pay-As-You-Go Gemini tier to remove the 5 RPM constraint in public staging environments.

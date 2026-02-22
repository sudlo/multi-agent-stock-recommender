# Multi-Agent Stock Recommendation System

Multi-agent AI system for stock recommendations using **LangGraph** (agent orchestration), **Bright Data MCP** (real-time web scraping), and **FastAPI** (API server).

Inspired by Keerti Purswani's YouTube tutorial:  
https://www.youtube.com/watch?v=NF2aRqIlYNE (from ~8:00 onwards – code, API keys, MCP setup, agents).

## Features
- Supervisor agent delegates tasks to 4 specialized agents  
- Stock selection (e.g., promising Nifty 50/large cap names)  
- Market data retrieval (prices, history, volume)  
- News & sentiment analysis  
- Final buy/sell recommendation with target price  
- Real-time data via Bright Data MCP tools  
- Secure API key handling with `.env`  
- FastAPI endpoint `/recommend`  
- Docker support for easy deployment

## Prerequisites
- Python 3.10+  
- [OpenAI API key](https://platform.openai.com/account/api-keys)  
- [Bright Data API token](https://brightdata.com/) (required for MCP scraping)

## Local Run (without Docker)

```bash
# 1. Clone the repo (after you add the other files)
git clone https://github.com/sudlo/multi-agent-stock-recommender.git
cd multi-agent-stock-recommender

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up secrets
cp .env.example .env
# Edit .env and fill your keys:
# OPENAI_API_KEY=sk-...
# BRIGHT_DATA_API_TOKEN=your-brightdata-token-here
# Optional: WEB_UNBLOCKER_ZONE=your-zone-if-needed

# 4. Start the server
uvicorn app:app --reload --port 8000

Test it (local)
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Recommend good stocks from Nifty 50 right now"}'

Or open in browser:
http://localhost:8000/docs (interactive Swagger UI)

Docker (recommended)
# Build the image
docker build -t stock-reco .

# Run the container
docker run -d -p 8000:8000 --env-file .env --name stock-reco stock-reco

Test it (Docker)
Same commands as local:

curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Recommend good stocks from Nifty 50 right now"}'

Or open: http://localhost:8000/docs
To see logs:
docker logs -f stock-reco
To stop:
docker stop stock-reco


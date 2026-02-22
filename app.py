import os
import logging
from typing import Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate required environment variables
required_keys = ["OPENAI_API_KEY", "BRIGHT_DATA_API_TOKEN"]
for key in required_keys:
    if not os.getenv(key):
        raise ValueError(f"Missing required env var: {key}")

# Initialize LLM (using a cheaper model for faster testing; change to gpt-4o if needed)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# Bright Data MCP configuration (stdio transport, as shown in the video)
mcp_config = {
    "mcp_servers": [
        {
            "name": "brightdata",
            "transport": "stdio",
            "command": [
                "npx",
                "@brightdata/mcp-server@latest",
                "--token",
                os.getenv("BRIGHT_DATA_API_TOKEN")
            ]
        }
    ]
}

# Initialize MCP client and load tools
try:
    mcp_client = MultiServerMCPClient.from_config(mcp_config)
    tools = mcp_client.get_tools()
    logger.info(f"Loaded {len(tools)} MCP tools from Bright Data")
except Exception as e:
    logger.error(f"Failed to load MCP tools: {e}")
    tools = []

# FastAPI app
app = FastAPI(title="Multi-Agent Stock Recommender")

class Query(BaseModel):
    query: str

@app.post("/recommend")
async def recommend(q: Query):
    if not tools:
        raise HTTPException(status_code=503, detail="MCP tools unavailable - check BRIGHT_DATA_API_TOKEN")

    try:
        result: Dict[str, Any] = {"query": q.query, "steps": {}}

        # Simple sequential agent chain (video-style react agents)
        # Agent 1: Stock selection
        stock_prompt = f"""
        {q.query}
        Recommend 2-4 promising large-cap or Nifty 50 stocks.
        Avoid penny stocks. Return JSON only.
        """
        stock_agent = create_react_agent(llm, tools)
        stock_res = stock_agent.invoke({"messages": [{"role": "user", "content": stock_prompt}]})
        result["steps"]["stock_selection"] = stock_res["messages"][-1].content

        # You can add more agents here (market data, news, recommendation) in similar way

        return result

    except Exception as e:
        logger.exception("Error during recommendation")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "mcp_tools_loaded": len(tools) > 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

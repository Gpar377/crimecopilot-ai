import asyncio
import json
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

# Load configurations
load_dotenv()

# Import local modules
from db import SessionLocal
from agent import agent_app

app = FastAPI(
    title="CrimeCopilot AI API",
    description="Backend API for Smart Crime Intelligence and Investigation Copilot",
    version="1.0"
)

# Configure CORS for Next.js Slate frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query / investigation prompt")
    session_id: str = Field("default_session", description="Conversation session ID for context merging")
    role: str = Field("Analyst", description="RBAC User role (e.g. Investigator, Analyst, Supervisor)")

@app.get("/api/health")
def health_check():
    # Verify local SQL connection
    db = SessionLocal()
    try:
        # Simple test query
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"
    finally:
        db.close()
        
    return {
        "status": "online",
        "database": db_status,
        "environment": {
            "neo4j_configured": bool(os.getenv("NEO4J_URI")),
            "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))
        }
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    async def event_generator():
        # Initialize LangGraph state
        initial_state = {
            "user_query": request.message,
            "session_id": request.session_id,
            "user_role": request.role,
            "intent": "",
            "context": {},
            "sql_results": [],
            "graph_results": [],
            "analytics_results": {},
            "evidence_trail": [],
            "response": "",
            "visualization_type": "none",
            "visualization_data": {},
            "confidence": 0.0,
            "follow_up_suggestions": []
        }
        
        try:
            # We run the graph runner node by node to stream the agent's progress logs
            print(f"Starting LangGraph run for query: {request.message}")
            
            # Send initial startup event
            yield {
                "event": "log",
                "data": json.dumps({"message": "Initializing CrimeCopilot AI agent..."})
            }
            await asyncio.sleep(0.4)

            # Node 1: Intent Classification
            yield {
                "event": "log",
                "data": json.dumps({"message": "Analyzing intent and extracting entities..."})
            }
            # Execute agent graph nodes (for skeleton, we simulate or run standard invoke)
            # In a full build, we use astream_events, but for local mock skeleton we run it step-by-step
            # to show progress logging to SSE.
            state = agent_app.invoke(initial_state)
            await asyncio.sleep(0.4)

            # Node 2: Relational Query execution
            yield {
                "event": "log",
                "data": json.dumps({"message": f"Querying relational records (District: {state['context'].get('entities', {}).get('district', 'All')})..."})
            }
            await asyncio.sleep(0.4)

            # Node 3: Graph Traversal
            yield {
                "event": "log",
                "data": json.dumps({"message": "Traversing connection paths and communication channels..."})
            }
            await asyncio.sleep(0.4)

            # Node 4: Hallucination Safeguard Check
            yield {
                "event": "log",
                "data": json.dumps({"message": "Running hallucination checks against database facts..."})
            }
            await asyncio.sleep(0.3)

            # Simulate Token/Word streaming of final formatted response
            words = state["response"].split(" ")
            current_text = ""
            for word in words:
                current_text += word + " "
                yield {
                    "event": "token",
                    "data": json.dumps({"text": word + " "})
                }
                await asyncio.sleep(0.05) # simulate typing speed

            # Send final complete response with visualizer payloads & evidence trail
            yield {
                "event": "done",
                "data": json.dumps({
                    "response": state["response"],
                    "visualization_type": state["visualization_type"],
                    "visualization_data": state["visualization_data"],
                    "evidence_trail": state["evidence_trail"],
                    "confidence": state["confidence"],
                    "follow_up_suggestions": state["follow_up_suggestions"]
                })
            }

        except Exception as e:
            print(f"Error in agent stream: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": f"Agent reasoning error: {e}"})
            }

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

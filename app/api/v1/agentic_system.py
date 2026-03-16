from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.ai_agents.workflow import process_query_agentic
# Add any authentication dependencies if needed (omitted for brevity)

router = APIRouter(prefix="/agents", tags=["Agentic MAS"])

class AgentQueryRequest(BaseModel):
    query: str

class AgentQueryResponse(BaseModel):
    response: str

@router.post("/query", response_model=AgentQueryResponse)
async def query_agentic_system(payload: AgentQueryRequest):
    """
    Submit a plain text query to the Multi-Agent System.
    This bypasses traditional CRUD and uses LangGraph + CrewAI to intelligently
    route to Project, Finance, or Forecast agents using Gemini.
    """
    try:
        if not payload.query:
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
            
        result = process_query_agentic(payload.query)
        return AgentQueryResponse(response=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter
from pydantic import BaseModel
from app.models.api_models import ChatRequest, ChatThreadRequest
from app.services.weather_agent_service import WeatherAgentService
from app.services.chat_agent_service import ChatAgentService
router = APIRouter()


weather_service = WeatherAgentService()
chat_agent_service = ChatAgentService()

class WorkflowInput(BaseModel):
    data: str

class Message(BaseModel):
    query: str

@router.post("/weather")
async def run_weather_workflow(input_data: ChatRequest):
    """
    POST endpoint for executing a weather workflow.
    """
    result = await weather_service.run_weather(input_data)
    return {"result": result}

@router.post("/agent/weather")
async def run_weather_workflow(input_data: ChatThreadRequest):
    """
    POST endpoint for executing a weather workflow.
    """
    result = await weather_service.run_weather_agent(input_data)
    return {"result": result}

@router.post("/agent/chat")
async def run_weather_workflow(input_data: ChatThreadRequest):
    """
    POST endpoint for executing a weather workflow.
    """
    result = await chat_agent_service.run_chat_sk(input_data)
    return {"result": result}
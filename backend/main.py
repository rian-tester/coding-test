from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from middleware.timing import TimingMiddleware
from services.ai_router import AIRouter
from services.rag_service import RAGService
from services.chat_service import ChatService
from services.data_service import DataService
from models.schemas import QuestionRequest, AIResponse, RouteType
from utils.logger import logger
import uvicorn
import os
import time
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="InterOpera API",
    description="AI-powered sales assistant with modular architecture and intelligent routing",
    version="2.0.0",
    contact={
        "name": "InterOpera Support",
        "url": "http://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

app.add_middleware(TimingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("images"):
    app.mount("/images", StaticFiles(directory="images"), name="images")

def initialize_server():
    logger.log_sync("SERVER", "STARTUP_BEGIN", extra="Initializing InterOpera API Server v2.0")
    
    python_version = f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
    logger.log_sync("SERVER", "ENVIRONMENT", extra=f"Python {python_version}")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        logger.log_sync("SERVER", "CONFIG_ERROR", extra="OPENAI_API_KEY not found")
        raise RuntimeError("OPENAI_API_KEY is not set in environment variables")
    
    logger.log_sync("SERVER", "CONFIG_SUCCESS", extra="OPENAI_API_KEY loaded")
    
    data_service = DataService()
    sales_data = data_service.get_sales_data()
    
    def load_system_instruction():
        try:
            with open("assistant.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "You are a helpful AI assistant for InterOpera sales support."
    
    system_instruction = load_system_instruction()
    
    ai_router = AIRouter(OPENAI_API_KEY)
    rag_service = RAGService(OPENAI_API_KEY, sales_data)
    chat_service = ChatService(OPENAI_API_KEY, system_instruction)
    
    logger.log_sync("SERVER", "SERVICES_INITIALIZED", extra="All services ready")
    logger.log_sync("SERVER", "STARTUP_COMPLETE", extra="InterOpera API Server v2.0 ready")
    
    return ai_router, rag_service, chat_service, data_service

ai_router, rag_service, chat_service, data_service = initialize_server()

api_sales_reps_doc = """
Retrieve sales representatives data.

**Response:**
- `200 OK`: JSON object with sales representatives data

**Example Response:**
```json
{
    "salesReps": [
        {
            "id": "1",
            "name": "Alice Smith",
            "role": "Senior Sales Manager",
            "region": "North America"
        }
    ]
}
```
"""

@app.get("/api/sales-reps", summary="Get Sales Representatives", tags=["Sales Data"], description=api_sales_reps_doc)
async def get_sales_reps(request: Request):
    timing_context = request.state.timing_context
    timing_context.log_event("DATA_RETRIEVAL", "Fetching sales reps data")
    
    return data_service.get_sales_data()

api_ai_doc = """
AI-powered question answering with intelligent routing.

**Features:**
- Automatic question classification (sales vs general)
- RAG-powered sales data queries
- General knowledge responses
- Performance logging and monitoring

**Request Body:**
- `question` (str): User question

**Responses:**
- `200 OK`: AI-generated answer with metadata
- `400 Bad Request`: Empty question
- `500 Internal Server Error`: Processing error

**Example Request:**
```json
{
    "question": "Who are the top sales representatives?"
}
```

**Example Response:**
```json
{
    "answer": "Based on the sales data, our top representatives are...",
    "route_type": "sales",
    "processing_time": 1.234
}
```
"""

@app.post("/api/ai", summary="AI Question Answering", tags=["AI"], description=api_ai_doc)
async def ai_endpoint(request: Request, question_request: QuestionRequest):
    timing_context = request.state.timing_context
    question = question_request.question.strip()
    session_id = request.state.session_id
    
    timing_context.log_input_received(question, len(question))
    
    if not question:
        timing_context.log_event("ERROR", "Empty question provided")
        raise HTTPException(status_code=400, detail="The 'question' field cannot be empty.")

    try:
        total_start_time = time.time()
        
        route_decision = await ai_router.route_question(question, session_id)
        
        if route_decision.route_type == RouteType.SALES:
            timing_context.log_event("ROUTE_DECISION", "SALES_RAG_PATH")
            answer = await rag_service.process_sales_question(question, session_id)
        else:
            timing_context.log_event("ROUTE_DECISION", "GENERAL_CHAT_PATH")
            answer = await chat_service.process_general_question(question, session_id)
        
        total_duration = time.time() - total_start_time
        timing_context.log_response_ready(len(answer))
        
        response = AIResponse(
            answer=answer,
            route_type=route_decision.route_type.value,
            processing_time=round(total_duration, 3)
        )
        
        return response
        
    except Exception as e:
        logger.log_sync(session_id, "AI_ENDPOINT_ERROR", extra=f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process the AI request. Please try again later.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.log_sync("SERVER", "SHUTDOWN_BEGIN", extra="InterOpera API Server shutting down")

if __name__ == "__main__":
    logger.log_sync("SERVER", "STARTUP_UVICORN", extra="Starting Uvicorn server on 0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

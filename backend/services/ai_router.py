import json
import time
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from models.schemas import RouteDecision, RouteType
from utils.logger import logger

class AIRouter:
    def __init__(self, openai_api_key: str):
        self.router_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=openai_api_key,
            temperature=0.1,
            max_completion_tokens=100
        )
        
        self.routing_prompt = PromptTemplate(
            input_variables=["question"],
            template=(
                "Analyze this user question and determine if it's about:\n"
                "1. SALES - questions about sales representatives, clients, deals, performance, or company sales data\n"
                "2. GENERAL - general questions, greetings, explanations, or topics unrelated to sales data\n\n"
                "Question: {question}\n\n"
                "Respond with ONLY one word: either 'sales' or 'general'"
            )
        )
        
        self.router_chain = self.routing_prompt | self.router_model

    async def route_question(self, question: str, session_id: str) -> RouteDecision:
        start_time = time.time()
        
        try:
            logger.log_sync(session_id, "AI_ROUTING_START", extra=f"Analyzing: {question[:30]}...")
            
            response = self.router_chain.invoke({"question": question})
            route_text = response.content.strip().lower()
            
            duration = time.time() - start_time
            
            if "sales" in route_text:
                route_type = RouteType.SALES
                confidence = 0.9
            elif "general" in route_text:
                route_type = RouteType.GENERAL
                confidence = 0.9
            else:
                route_type = RouteType.GENERAL
                confidence = 0.5
                logger.log_sync(session_id, "AI_ROUTING_FALLBACK", extra=f"Unclear response: {route_text}")
            
            logger.log_sync(session_id, "AI_ROUTING_COMPLETE", duration, f"Route: {route_type.value} | Confidence: {confidence}")
            
            return RouteDecision(
                route_type=route_type,
                confidence=confidence,
                reasoning=f"AI classified as {route_type.value} in {duration:.3f}s"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.log_sync(session_id, "AI_ROUTING_ERROR", duration, f"Error: {str(e)}")
            
            return RouteDecision(
                route_type=RouteType.GENERAL,
                confidence=0.3,
                reasoning=f"Routing failed, defaulting to general: {str(e)}"
            )

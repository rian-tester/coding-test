import json
import time
from typing import Dict, Any, List, Set
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from models.schemas import RouteDecision, RouteType
from utils.logger import logger
from services.conversation_memory import conversation_memory

class AIRouter:
    def __init__(self, openai_api_key: str, sales_data: Dict[str, Any]):
        self.router_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=openai_api_key,
            temperature=0.1,
            max_completion_tokens=100
        )
        
        self.sales_keywords = self._extract_sales_keywords(sales_data)
        logger.log_sync("AI_ROUTER", "KEYWORDS_EXTRACTED", extra=f"Loaded {len(self.sales_keywords)} sales keywords")
        
        self.routing_prompt = PromptTemplate(
            input_variables=["question", "conversation_history", "sales_keywords"],
            template=(
                "You are a smart routing system for a sales data assistant.\n\n"
                "SALES DATABASE KEYWORDS: {sales_keywords}\n\n"
                "ROUTING RULES:\n"
                "1. If the question mentions ANY keyword from the sales database → Route: 'sales'\n"
                "2. If the question is about sales reps, clients, deals, performance → Route: 'sales'\n"
                "3. Otherwise for general questions → Route: 'general'\n\n"
                "Previous conversation context:\n{conversation_history}\n\n"
                "Current question: {question}\n\n"
                "Respond with ONLY one word: either 'sales' or 'general'"
            )
        )
        
        self.router_chain = self.routing_prompt | self.router_model
    
    def _extract_sales_keywords(self, sales_data: Dict[str, Any]) -> Set[str]:
        keywords = set()
        
        for rep in sales_data.get("salesReps", []):
            keywords.add(rep["name"].lower())
            keywords.add(rep["role"].lower()) 
            keywords.add(rep["region"].lower())
            
            for skill in rep.get("skills", []):
                keywords.add(skill.lower())
            
            for client in rep.get("clients", []):
                keywords.add(client["name"].lower())
                keywords.add(client["industry"].lower())
            
            for deal in rep.get("deals", []):
                keywords.add(deal["client"].lower())
                keywords.add(deal["status"].lower())
        
        return keywords

    async def route_question(self, question: str, session_id: str) -> RouteDecision:
        start_time = time.time()
        
        try:
            logger.log_sync(session_id, "AI_ROUTING_START", extra=f"Analyzing: {question[:30]}...")
            
            question_lower = question.lower()
            
            direct_keyword_match = any(keyword in question_lower for keyword in self.sales_keywords)
            
            if direct_keyword_match:
                duration = time.time() - start_time
                logger.log_sync(session_id, "DIRECT_KEYWORD_MATCH", duration, f"Found sales keyword in: {question[:50]}")
                
                return RouteDecision(
                    route_type=RouteType.SALES,
                    confidence=0.95,
                    reasoning=f"Direct keyword match found in {duration:.3f}s"
                )
            
            conversation_history = await conversation_memory.get_conversation_context(session_id)
            keywords_str = ", ".join(sorted(list(self.sales_keywords)[:20]))
            
            response = self.router_chain.invoke({
                "question": question,
                "conversation_history": conversation_history or "No previous conversation",
                "sales_keywords": keywords_str
            })
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

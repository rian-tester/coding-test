import json
import time
import faiss
import numpy as np
import re
from typing import List, Dict, Any, Set
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from functools import lru_cache
from models.schemas import SalesRepData
from utils.logger import logger
from services.conversation_memory import conversation_memory

class RAGService:
    def __init__(self, openai_api_key: str, sales_data: Dict[str, Any]):
        self.sales_data = sales_data
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        self.rag_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=openai_api_key,
            temperature=0.3,
            max_completion_tokens=800
        )
        
        self.rag_prompt = PromptTemplate(
            input_variables=["question", "sales_data", "conversation_history"],
            template=(
                "You are a sales data assistant. Answer the question using the provided sales data.\n\n"
                "Previous conversation:\n{conversation_history}\n\n"
                "Sales Data:\n{sales_data}\n\n"
                "Current question: {question}\n\n"
                "If multiple people are mentioned in the question, provide information about ALL of them. "
                "Organize your response clearly for each person mentioned. "
                "Provide a concise, accurate answer based on the sales data and conversation context:"
            )
        )
        
        self.rag_chain = self.rag_prompt | self.rag_model
        
        self.sales_chunks = []
        self.sales_index = None
        self.sales_metadata = []
        self.cache = {}
        self.sales_keywords = set()
        
        self._initialize_vector_store()
        self._extract_sales_keywords()

    def _extract_sales_keywords(self):
        for rep in self.sales_data.get("salesReps", []):
            name_parts = rep["name"].lower().split()
            self.sales_keywords.update(name_parts)
            
            self.sales_keywords.add(rep["role"].lower())
            self.sales_keywords.add(rep["region"].lower())
            
            for skill in rep.get("skills", []):
                self.sales_keywords.add(skill.lower())
            
            for client in rep.get("clients", []):
                self.sales_keywords.add(client["name"].lower())
            
            for deal in rep.get("deals", []):
                self.sales_keywords.add(deal["client"].lower())

    def _extract_mentioned_names(self, question: str) -> Set[str]:
        question_lower = question.lower()
        mentioned_keywords = set()
        
        for keyword in self.sales_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', question_lower):
                mentioned_keywords.add(keyword)
        
        return mentioned_keywords

    def _initialize_vector_store(self):
        self.sales_chunks, self.sales_metadata = self._create_sales_chunks()
        
        if self.sales_chunks:
            embeddings = self.embedding_model.encode(self.sales_chunks)
            dimension = embeddings.shape[1]
            self.sales_index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(embeddings)
            self.sales_index.add(embeddings.astype('float32'))

    def _create_sales_chunks(self):
        chunks = []
        metadata = []
        
        for rep in self.sales_data.get("salesReps", []):
            profile_text = f"Sales Rep: {rep['name']}, Role: {rep['role']}, Region: {rep['region']}, Skills: {', '.join(rep['skills'])}"
            chunks.append(profile_text)
            metadata.append({"type": "profile", "rep_id": rep["id"], "rep_name": rep["name"]})
            
            if rep.get("deals"):
                deals_text = f"{rep['name']} deals: "
                for deal in rep["deals"]:
                    deals_text += f"Client {deal['client']} - ${deal['value']} - {deal['status']}; "
                chunks.append(deals_text)
                metadata.append({"type": "deals", "rep_id": rep["id"], "rep_name": rep["name"]})
            
            if rep.get("clients"):
                clients_text = f"{rep['name']} clients: "
                for client in rep["clients"]:
                    clients_text += f"{client['name']} ({client['industry']}) - {client['contact']}; "
                chunks.append(clients_text)
                metadata.append({"type": "clients", "rep_id": rep["id"], "rep_name": rep["name"]})
        
        return chunks, metadata

    @lru_cache(maxsize=100)
    def _search_sales_data(self, question: str, top_k: int = 5) -> str:
        if self.sales_index is None or not self.sales_chunks:
            return json.dumps(self.sales_data.get("salesReps", [])[:2])
        
        cache_key = f"{question.lower().strip()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        mentioned_keywords = self._extract_mentioned_names(question)
        relevant_info = set()
        
        if mentioned_keywords:
            for keyword in mentioned_keywords:
                keyword_results = self._search_by_keyword(keyword, top_k=3)
                relevant_info.update(keyword_results)
        
        if not relevant_info:
            query_embedding = self.embedding_model.encode([question])
            faiss.normalize_L2(query_embedding)
            scores, indices = self.sales_index.search(query_embedding.astype('float32'), top_k)
            
            for i, idx in enumerate(indices[0]):
                if scores[0][i] > 0.25:
                    chunk = self.sales_chunks[idx]
                    relevant_info.add(chunk)
        
        result = "\n".join(list(relevant_info)[:6]) if relevant_info else "Limited sales rep data available."
        self.cache[cache_key] = result
        return result
    
    def _search_by_keyword(self, keyword: str, top_k: int = 3) -> List[str]:
        matching_chunks = []
        
        for i, chunk in enumerate(self.sales_chunks):
            if re.search(r'\b' + re.escape(keyword) + r'\b', chunk.lower()):
                matching_chunks.append(chunk)
                if len(matching_chunks) >= top_k:
                    break
        
        return matching_chunks

    async def process_sales_question(self, question: str, session_id: str) -> str:
        start_time = time.time()
        
        logger.log_sync(session_id, "RAG_SEARCH_START", extra="Searching sales data")
        
        sales_data = self._search_sales_data(question, top_k=5)
        
        search_duration = time.time() - start_time
        logger.log_sync(session_id, "RAG_SEARCH_END", search_duration, f"Retrieved {len(sales_data)} chars")
        
        if len(sales_data) > 3000:
            sales_data = sales_data[:2500]
            logger.log_sync(session_id, "RAG_DATA_TRUNCATED", extra="Data truncated to 2500 chars")
        
        openai_start = time.time()
        logger.log_sync(session_id, "RAG_OPENAI_START", extra="Generating response")
        
        conversation_history = await conversation_memory.get_conversation_context(session_id)
        
        response = self.rag_chain.invoke({
            "question": question,
            "sales_data": sales_data,
            "conversation_history": conversation_history or "No previous conversation"
        })
        
        openai_duration = time.time() - openai_start
        logger.log_sync(session_id, "RAG_OPENAI_END", openai_duration, f"Response generated")
        
        return response.content if hasattr(response, "content") else str(response)

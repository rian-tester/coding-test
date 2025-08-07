import json
import time
import faiss
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from functools import lru_cache
from models.schemas import SalesRepData
from utils.logger import logger

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
            input_variables=["question", "sales_data"],
            template=(
                "You are a sales data assistant. Answer the question using the provided sales data.\n\n"
                "Sales Data:\n{sales_data}\n\n"
                "Question: {question}\n\n"
                "Provide a concise, accurate answer based on the sales data:"
            )
        )
        
        self.rag_chain = self.rag_prompt | self.rag_model
        
        self.sales_chunks = []
        self.sales_index = None
        self.sales_metadata = []
        self.cache = {}
        
        self._initialize_vector_store()

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
    def _search_sales_data(self, question: str, top_k: int = 2) -> str:
        if self.sales_index is None or not self.sales_chunks:
            return json.dumps(self.sales_data.get("salesReps", [])[:2])
        
        cache_key = f"{question.lower().strip()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        query_embedding = self.embedding_model.encode([question])
        faiss.normalize_L2(query_embedding)
        
        scores, indices = self.sales_index.search(query_embedding.astype('float32'), top_k)
        
        relevant_info = []
        for i, idx in enumerate(indices[0]):
            if scores[0][i] > 0.25:
                chunk = self.sales_chunks[idx]
                relevant_info.append(chunk)
                
                if len(relevant_info) >= 2:
                    break
        
        result = "\n".join(relevant_info) if relevant_info else "Limited sales rep data available."
        self.cache[cache_key] = result
        return result

    async def process_sales_question(self, question: str, session_id: str) -> str:
        start_time = time.time()
        
        logger.log_sync(session_id, "RAG_SEARCH_START", extra="Searching sales data")
        
        sales_data = self._search_sales_data(question, top_k=2)
        
        search_duration = time.time() - start_time
        logger.log_sync(session_id, "RAG_SEARCH_END", search_duration, f"Retrieved {len(sales_data)} chars")
        
        if len(sales_data) > 3000:
            sales_data = sales_data[:1000]
            logger.log_sync(session_id, "RAG_DATA_TRUNCATED", extra="Data truncated to 1000 chars")
        
        openai_start = time.time()
        logger.log_sync(session_id, "RAG_OPENAI_START", extra="Generating response")
        
        response = self.rag_chain.invoke({
            "question": question,
            "sales_data": sales_data
        })
        
        openai_duration = time.time() - openai_start
        logger.log_sync(session_id, "RAG_OPENAI_END", openai_duration, f"Response generated")
        
        return response.content if hasattr(response, "content") else str(response)

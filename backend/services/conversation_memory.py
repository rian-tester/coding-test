from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass

@dataclass
class ConversationExchange:
    user_message: str
    ai_response: str
    timestamp: datetime

class ConversationMemory:
    def __init__(self, max_exchanges_per_session: int = 5, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, List[ConversationExchange]] = {}
        self.session_timestamps: Dict[str, datetime] = {}
        self.max_exchanges = max_exchanges_per_session
        self.timeout_minutes = session_timeout_minutes
        
    async def add_exchange(self, session_id: str, user_message: str, ai_response: str):
        await self._cleanup_expired_sessions()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        exchange = ConversationExchange(
            user_message=user_message,
            ai_response=ai_response,
            timestamp=datetime.now()
        )
        
        self.sessions[session_id].append(exchange)
        self.session_timestamps[session_id] = datetime.now()
        
        if len(self.sessions[session_id]) > self.max_exchanges:
            self.sessions[session_id] = self.sessions[session_id][-self.max_exchanges:]
    
    async def get_conversation_context(self, session_id: str) -> str:
        await self._cleanup_expired_sessions()
        
        if session_id not in self.sessions or not self.sessions[session_id]:
            return ""
        
        context_parts = []
        for exchange in self.sessions[session_id]:
            context_parts.append(f"User: {exchange.user_message}")
            context_parts.append(f"Assistant: {exchange.ai_response}")
        
        return "\n".join(context_parts)
    
    async def has_session(self, session_id: str) -> bool:
        await self._cleanup_expired_sessions()
        return session_id in self.sessions and bool(self.sessions[session_id])
    
    async def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.session_timestamps:
            del self.session_timestamps[session_id]
    
    async def _cleanup_expired_sessions(self):
        cutoff_time = datetime.now() - timedelta(minutes=self.timeout_minutes)
        expired_sessions = [
            session_id for session_id, timestamp in self.session_timestamps.items()
            if timestamp < cutoff_time
        ]
        
        for session_id in expired_sessions:
            await self.clear_session(session_id)

conversation_memory = ConversationMemory()

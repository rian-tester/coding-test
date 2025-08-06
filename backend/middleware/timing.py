from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import asyncio
from utils.logger import generate_session_id, TimingContext, logger

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = generate_session_id()
        timing_context = TimingContext(session_id)
        
        request.state.session_id = session_id
        request.state.timing_context = timing_context
        
        method = request.method
        path = str(request.url.path)
        
        logger.log_sync(session_id, "REQUEST_START", extra=f"{method} {path}")
        
        response = await call_next(request)
        
        asyncio.create_task(timing_context.finish_async())
        
        return response

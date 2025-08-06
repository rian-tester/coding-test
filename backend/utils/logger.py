import asyncio
import time
from datetime import datetime
import uuid
import os

class APILogger:
    def __init__(self, log_file="api-log.txt"):
        self.log_file = log_file
        self.ensure_log_file()
        self._write_queue = None
        self._writer_task = None
        self._initialized = False
    
    def ensure_log_file(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write(f"=== API Log Started - {datetime.now()} ===\n")
                f.write("Format: TIMESTAMP | EVENT_TYPE | SESSION_ID | DURATION | DETAILS\n")
                f.write("="*80 + "\n")
    
    def _ensure_async_initialized(self):
        """Initialize async components if not already done"""
        if not self._initialized:
            try:
                loop = asyncio.get_running_loop()
                if self._write_queue is None:
                    self._write_queue = asyncio.Queue()
                if self._writer_task is None or self._writer_task.done():
                    self._writer_task = loop.create_task(self._background_writer())
                self._initialized = True
            except RuntimeError:
                # No running event loop, will init later when needed
                pass
    
    async def _background_writer(self):
        """Background task that handles file writing"""
        while True:
            try:
                log_entry = await self._write_queue.get()
                if log_entry is None:  # Shutdown signal
                    break
                
                def write_to_file():
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        f.write(log_entry)
                        f.flush()  # Ensure immediate write
                
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, write_to_file)
                self._write_queue.task_done()
            except Exception as e:
                print(f"Logger error: {e}")
    
    def format_log(self, session_id, event_type, duration=None, extra=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Include milliseconds
        
        if duration is not None:
            duration_str = f" | {duration:.3f}s"
        else:
            duration_str = " | -"
        
        extra_str = f" | {extra}" if extra else ""
        return f"{timestamp} | {event_type:<20} | {session_id}{duration_str}{extra_str}\n"
    
    def log_sync(self, session_id, event_type, duration=None, extra=None):
        log_entry = self.format_log(session_id, event_type, duration, extra)
        
        # Print to console immediately
        print(f"🔍 {log_entry.strip()}")
        
        # Write to file synchronously for critical events
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.flush()
        except Exception as e:
            print(f"Sync logging error: {e}")
    
    async def log_async(self, session_id, event_type, duration=None, extra=None):
        log_entry = self.format_log(session_id, event_type, duration, extra)
        
        # Print to console immediately
        print(f"🔍 {log_entry.strip()}")
        
        # Queue for background file writing
        try:
            self._ensure_async_initialized()
            if self._write_queue:
                await self._write_queue.put(log_entry)
            else:
                # Fallback to sync if async not available
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                    f.flush()
        except Exception as e:
            print(f"Async logging error: {e}")
            # Fallback to sync writing
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                    f.flush()
            except Exception as sync_error:
                print(f"Fallback logging error: {sync_error}")
    
    def log_api_call_details(self, session_id, method, path, user_agent=None, ip=None):
        """Log detailed API call information"""
        details = f"Method: {method}, Path: {path}"
        if user_agent:
            details += f", User-Agent: {user_agent[:50]}..."
        if ip:
            details += f", IP: {ip}"
        self.log_sync(session_id, "REQUEST_DETAILS", extra=details)
    
    def log_response_details(self, session_id, status_code, response_size=None):
        """Log response details"""
        details = f"Status: {status_code}"
        if response_size:
            details += f", Size: {response_size} bytes"
        self.log_sync(session_id, "RESPONSE_DETAILS", extra=details)
    
    async def shutdown(self):
        """Gracefully shutdown the logger"""
        if self._write_queue:
            await self._write_queue.put(None)  # Shutdown signal
        if self._writer_task:
            await self._writer_task

logger = APILogger()

def generate_session_id():
    return str(uuid.uuid4())[:8]

class TimingContext:
    def __init__(self, session_id):
        self.session_id = session_id
        self.start_time = time.time()
        self.events = []
        self.route_type = None
        self.openai_calls = 0
        self.rag_calls = 0
        self.context_retrieval_calls = 0
    
    def log_event(self, event_type, extra=None):
        current_time = time.time()
        duration_since_start = current_time - self.start_time
        
        # Track specific event types
        if event_type == "OPENAI_START":
            self.openai_calls += 1
        elif event_type == "RAG_START":
            self.rag_calls += 1
        elif event_type == "CONTEXT_RETRIEVAL_START":
            self.context_retrieval_calls += 1
        elif event_type == "ROUTING_DECISION":
            self.route_type = extra
        
        logger.log_sync(self.session_id, event_type, duration_since_start, extra)
        self.events.append((event_type, current_time, extra))
    
    def log_duration_event(self, event_type, start_time, extra=None):
        current_time = time.time()
        duration = current_time - start_time
        duration_since_start = current_time - self.start_time
        
        # Create detailed duration info
        duration_info = f"took {duration:.3f}s"
        if extra:
            duration_info += f" | {extra}"
        
        logger.log_sync(self.session_id, event_type, duration_since_start, duration_info)
        self.events.append((event_type, current_time, duration_info))
    
    def log_input_received(self, question, question_length):
        """Log when input is received"""
        extra = f"Question length: {question_length} chars | Preview: {question[:50]}..."
        logger.log_sync(self.session_id, "INPUT_RECEIVED", 0.0, extra)
    
    def log_response_ready(self, response_length):
        """Log when response is ready to send"""
        duration_since_start = time.time() - self.start_time
        extra = f"Response length: {response_length} chars"
        logger.log_sync(self.session_id, "RESPONSE_READY", duration_since_start, extra)
    
    async def finish_async(self, status_code=200, response_size=None):
        """Enhanced finish method with detailed summary"""
        total_duration = time.time() - self.start_time
        
        # Create summary details
        summary = f"Route: {self.route_type or 'Unknown'}"
        summary += f" | OpenAI calls: {self.openai_calls}"
        summary += f" | RAG calls: {self.rag_calls}"
        summary += f" | Context calls: {self.context_retrieval_calls}"
        summary += f" | Status: {status_code}"
        if response_size:
            summary += f" | Response size: {response_size} bytes"
        
        await logger.log_async(self.session_id, "REQUEST_COMPLETE", total_duration, summary)
        
        # Log a separator for readability
        await logger.log_async(self.session_id, "---", None, "End of request")
    
    def get_performance_summary(self):
        """Get a summary of performance metrics"""
        total_duration = time.time() - self.start_time
        return {
            "session_id": self.session_id,
            "total_duration": total_duration,
            "route_type": self.route_type,
            "openai_calls": self.openai_calls,
            "rag_calls": self.rag_calls,
            "context_retrieval_calls": self.context_retrieval_calls,
            "event_count": len(self.events)
        }

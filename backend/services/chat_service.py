import time
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from utils.logger import logger

class ChatService:
    def __init__(self, openai_api_key: str, system_instruction: str):
        self.system_instruction = system_instruction
        
        self.chat_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=openai_api_key,
            temperature=0.7,
            max_completion_tokens=800
        )
        
        self.chat_prompt = PromptTemplate(
            input_variables=["system_instruction", "question"],
            template=(
                "{system_instruction}\n\n"
                "User question: {question}\n\n"
                "Provide a helpful, clear response:"
            )
        )
        
        self.chat_chain = self.chat_prompt | self.chat_model

    async def process_general_question(self, question: str, session_id: str) -> str:
        start_time = time.time()
        
        logger.log_sync(session_id, "CHAT_OPENAI_START", extra="Processing general question")
        
        try:
            response = self.chat_chain.invoke({
                "system_instruction": self.system_instruction,
                "question": question
            })
            
            duration = time.time() - start_time
            logger.log_sync(session_id, "CHAT_OPENAI_END", duration, "General response generated")
            
            return response.content if hasattr(response, "content") else str(response)
            
        except Exception as e:
            duration = time.time() - start_time
            logger.log_sync(session_id, "CHAT_OPENAI_ERROR", duration, f"Error: {str(e)}")
            raise e

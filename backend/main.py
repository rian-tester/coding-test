from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI
import logging
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import tiktoken
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np




# Initialize FastAPI app
app = FastAPI(
    title="InterOpera API",
    description="This is the backend API for the InterOpera project. It provides endpoints for managing sales representatives and AI-powered question answering.",
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the "images" directory
app.mount("/images", StaticFiles(directory="images"), name="images")

# Load dummy data
with open("dummyData.json", "r") as f:
    DUMMY_DATA = json.load(f)

# Load environment variables
load_dotenv()

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment variables.")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize LangChain Chat Model
chat_model = ChatOpenAI(
    model="gpt-4",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.7,
    max_completion_tokens=1000  # Reduced to leave room for input tokens
)

# Load system instruction from assistant.txt
def load_system_instruction():
    with open("assistant.txt", "r") as f:
        return f.read().strip()

# Create a LangChain PromptTemplate
system_instruction = load_system_instruction()
prompt_template = PromptTemplate(
    input_variables=["history_messages", "question", "data"],
    template=(
        "{system_instruction}\n\n"
        "Conversation history:\n"
        "{history_messages}\n\n"
        "The user asked: {question}\n"
        "Here is the relevant data: {data}\n"
        "Please provide a clean, human-readable, and elaborated response."
    )
)

# Chain the PromptTemplate and ChatOpenAI using the `|` operator
llm_chain = prompt_template | chat_model

# Session store to maintain conversation history
session_store = {}

def get_session_history(session_id):
    """
    Retrieve or initialize the message history for a given session ID.
    """
    if session_id not in session_store:
        logging.debug(f"Creating new session history for session_id: {session_id}")
        session_store[session_id] = ChatMessageHistory()
    else:
        logging.debug(f"Retrieving existing session history for session_id: {session_id}")
    return session_store[session_id]


# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler("error.log"),  # Logs to a file
    ],
)

# Function to check if the question is related to dummy data
def is_related_to_dummy_data(question):
    keywords = [
        "sales reps", "sales representatives", "dummy data", "sales team",
        "salesperson", "sales rep", "sales executive", "sales manager"
    ]
    return any(keyword in question.lower() for keyword in keywords)

# Function to generate a response from dummy data
def generate_dummy_data_response():
    sales_reps = DUMMY_DATA.get("salesReps", [])
    if not sales_reps:
        return "I couldn't find any sales representatives in the dummy data."
    response = "Here are the sales representatives from the dummy data:\n"
    response += "\n".join([f"- {rep}" for rep in sales_reps])
    return response

# Define the sales-rep doc
api_sales_reps_doc = """
    Retrieve a list of sales representatives and their details.

    **Response:**
    - `200 OK`: A JSON object containing the sales representatives' data.

    **Example Response:**
    ```json
    {
        "salesReps": [
            {
                "name": "John Doe",
                "role": "Regional Manager",
                "region": "North America",
                "clients": [
                    {"name": "Client A", "status": "Active"},
                    {"name": "Client B", "status": "Inactive"}
                ]
            }
        ]
    }
    ```
    """

@app.get("/api/sales-reps", summary="Get Sales Representatives", tags=["Sales Reps"], description=api_sales_reps_doc)
def get_sales_reps():
    
    return DUMMY_DATA


# Define the API doc
api_ai_doc = """
    Handles AI-powered question-answering requests.

    **Request Body:**
    - `question` (str): The question to be answered.

    **Responses:**
    - `200 OK`: A JSON object containing the AI-generated answer.
    - `400 Bad Request`: If the `question` field is empty.
    - `422 Unprocessable Entity`: If the request body is malformed or the `question` field is of an invalid type.
    - `500 Internal Server Error`: If an error occurs while processing the request.

    **Example Request:**
    ```json
    {
        "question": "Who are the sales reps?"
    }
    ```

    **Example Response:**
    ```json
    {
        "answer": "The sales representatives are John Doe and Jane Smith."
    }
    ```

    **Error Response (400):**
    ```json
    {
        "detail": "The 'question' field cannot be empty."
    }
    ```

    **Error Response (500):**
    ```json
    {
        "detail": "Failed to process the AI request. Please try again later."
    }
    ```
    """

# Define a Pydantic model for the request body
class AIRequest(BaseModel):
    question: str

def trim_history(messages, max_tokens=4096):
    """
    Trim the conversation history to fit within the token limit.
    """
    encoding = tiktoken.encoding_for_model("gpt-4")  # Use the appropriate model
    trimmed_messages = []
    total_tokens = 0

    # Reverse the messages to start from the most recent
    for msg in reversed(messages):
        # Estimate token count for the message
        token_count = len(encoding.encode(msg.content)) + 4  # +4 for metadata (role, etc.)
        if total_tokens + token_count > max_tokens:
            break
        trimmed_messages.insert(0, msg)  # Add to the beginning of the list
        total_tokens += token_count

    return trimmed_messages

# Initialize the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize FAISS index
dimension = 384  # Dimension of the embeddings from the model
index = faiss.IndexFlatL2(dimension)

# Store metadata (e.g., message content and type) alongside embeddings
conversation_metadata = []

def store_message(message, message_type):
    """
    Store a message in the vector store with its metadata.
    """
    global conversation_metadata

    # Generate embedding for the message
    embedding = embedding_model.encode([message])

    # Add the embedding to the FAISS index
    index.add(np.array(embedding, dtype=np.float32))

    # Store metadata
    conversation_metadata.append({"content": message, "type": message_type})


def retrieve_relevant_messages(query, top_k=5):
    """
    Retrieve the most relevant messages from the vector store.
    """
    # Generate embedding for the query
    query_embedding = embedding_model.encode([query])

    # Perform similarity search
    distances, indices = index.search(np.array(query_embedding, dtype=np.float32), top_k)

    # Retrieve the corresponding messages
    relevant_messages = [conversation_metadata[i] for i in indices[0] if i < len(conversation_metadata)]
    return relevant_messages


# Remove the RunnableWithMessageHistory wrapper and use llm_chain directly
@app.post("/api/ai", summary="AI Question Answering", tags=["AI"], description=api_ai_doc)
async def ai_endpoint(request: Request, ai_request: AIRequest):
    """
    Handles AI-powered question-answering requests with conversational memory.
    """
    question = ai_request.question.strip()
    session_id = request.headers.get("X-Session-ID", "default")  # Use a default session if none is provided
    logging.debug(f"Session ID: {session_id}")

    if not question:
        raise HTTPException(status_code=400, detail="The 'question' field cannot be empty.")

    try:
        # Store the user's question in the vector store
        store_message(question, "human")

        # Retrieve relevant messages from the vector store (increase top_k if needed)
        relevant_messages = retrieve_relevant_messages(question, top_k=5)

        # Format the retrieved messages for the prompt
        history_messages = "\n".join(
            f"{'User' if msg['type'] == 'human' else 'AI'}: {msg['content']}" for msg in relevant_messages
        )

        # Prepare the input for the chain
        input_data = {
            "history_messages": history_messages,
            "question": question,
            "data": "No specific data available.",
            "system_instruction": system_instruction,
        }

        # Add before invoking the LLM chain
        token_count = len(tiktoken.encoding_for_model("gpt-4").encode(
            input_data["system_instruction"] + input_data["history_messages"] + input_data["question"] + input_data["data"]))
        logging.debug(f"Total tokens in request: {token_count}")

        # Add before invoking the LLM chain
        MAX_ALLOWED_TOKENS = 7000  # Safe limit for GPT-4 (8192 - 1000 completion - buffer)

        if token_count > MAX_ALLOWED_TOKENS:
            # Reduce the number of history messages
            relevant_messages = relevant_messages[:3]  # Only use top 3 messages
            history_messages = "\n".join(
                f"{'User' if msg['type'] == 'human' else 'AI'}: {msg['content']}" for msg in relevant_messages
            )
            input_data["history_messages"] = history_messages

        # Check if the question is related to dummy data
        if is_related_to_dummy_data(question):
            sales_reps = DUMMY_DATA.get("salesReps", [])
            if not sales_reps:
                response = "I couldn't find any sales representatives in the dummy data."
            else:
                # Check for specific sales rep
                for rep in sales_reps:
                    if rep.get("name").lower() in question.lower():
                        input_data["data"] = json.dumps(rep)
                        break
                else:
                    input_data["data"] = json.dumps(sales_reps)

        # Use the llm_chain directly instead of chain_with_message_history
        response = llm_chain.invoke(input_data)

        # Ensure response is a string
        if hasattr(response, "content"):
            response = response.content  # Extract content if it's an AIMessage
        elif not isinstance(response, str):
            response = json.dumps(response)  # Convert to string if it's not

        # Store the AI's response in the vector store
        store_message(response, "ai")

        return {"answer": response}
    except Exception as e:
        logging.error(f"OpenAI API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process the AI request. Please try again later.")

@app.get("/api/debug/sessions")
def debug_sessions():
    return {session_id: history.messages for session_id, history in session_store.items()}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



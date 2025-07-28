from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from dotenv import load_dotenv
import logging
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import tiktoken
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from functools import lru_cache

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

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler("error.log"),  # Logs to a file
    ],
)

# Initialize the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize FAISS index for conversation history
dimension = 384  # Dimension of the embeddings from the model
index = faiss.IndexFlatL2(dimension)

# Store metadata (e.g., message content and type) alongside embeddings
conversation_metadata = []

# NEW: Sales Rep Optimization Variables
sales_rep_chunks = []
sales_rep_index = None
sales_rep_metadata = []
sales_rep_cache = {}

def create_sales_rep_chunks():
    """Create searchable text chunks from sales rep data - runs once on startup"""
    global sales_rep_chunks, sales_rep_metadata
    
    chunks = []
    metadata = []
    
    for rep in DUMMY_DATA.get("salesReps", []):
        # Profile chunk
        profile_text = f"Sales Rep: {rep['name']}, Role: {rep['role']}, Region: {rep['region']}, Skills: {', '.join(rep['skills'])}"
        chunks.append(profile_text)
        metadata.append({"type": "profile", "rep_id": rep["id"], "rep_name": rep["name"]})
        
        # Deals chunk
        if rep.get("deals"):
            deals_text = f"{rep['name']} deals: "
            for deal in rep["deals"]:
                deals_text += f"Client {deal['client']} - ${deal['value']} - {deal['status']}; "
            chunks.append(deals_text)
            metadata.append({"type": "deals", "rep_id": rep["id"], "rep_name": rep["name"]})
        
        # Clients chunk
        if rep.get("clients"):
            clients_text = f"{rep['name']} clients: "
            for client in rep["clients"]:
                clients_text += f"{client['name']} ({client['industry']}) - {client['contact']}; "
            chunks.append(clients_text)
            metadata.append({"type": "clients", "rep_id": rep["id"], "rep_name": rep["name"]})
    
    return chunks, metadata

def initialize_sales_rep_search():
    """Initialize FAISS index for sales rep data - runs once on startup"""
    global sales_rep_chunks, sales_rep_index, sales_rep_metadata
    
    sales_rep_chunks, sales_rep_metadata = create_sales_rep_chunks()
    
    if sales_rep_chunks:
        # Create embeddings
        embeddings = embedding_model.encode(sales_rep_chunks)
        
        # Initialize FAISS index for sales rep data
        sales_rep_index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        sales_rep_index.add(embeddings.astype('float32'))

@lru_cache(maxsize=50)
def search_sales_rep_data(question: str, top_k: int = 3) -> str:
    """Search for relevant sales rep information using semantic similarity"""
    if sales_rep_index is None or not sales_rep_chunks:
        return json.dumps(DUMMY_DATA.get("salesReps", []))
    
    # Check cache first
    cache_key = f"{question.lower().strip()}_{top_k}"
    if cache_key in sales_rep_cache:
        return sales_rep_cache[cache_key]
    
    # Create query embedding
    query_embedding = embedding_model.encode([question])
    faiss.normalize_L2(query_embedding)
    
    # Search for similar chunks
    scores, indices = sales_rep_index.search(query_embedding.astype('float32'), top_k)
    
    # Collect relevant information
    relevant_info = []
    seen_reps = set()
    
    for i, idx in enumerate(indices[0]):
        if scores[0][i] > 0.2:  # Similarity threshold
            chunk = sales_rep_chunks[idx]
            metadata = sales_rep_metadata[idx]
            rep_name = metadata["rep_name"]
            
            if rep_name not in seen_reps:
                seen_reps.add(rep_name)
                relevant_info.append(f"[{metadata['type'].upper()}] {chunk}")
    
    result = "\n".join(relevant_info) if relevant_info else json.dumps(DUMMY_DATA.get("salesReps", []))
    
    # Cache the result
    sales_rep_cache[cache_key] = result
    return result

# Initialize sales rep search on startup
initialize_sales_rep_search()

# Function to check if the question is related to dummy data
def is_related_to_dummy_data(question):
    keywords = [
        "sales reps", "sales representatives", "dummy data", "sales team",
        "salesperson", "sales rep", "sales executive", "sales manager",
        "alice", "bob", "charlie", "dana", "deals", "clients", "performance"
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
    
    if not question:
        raise HTTPException(status_code=400, detail="The 'question' field cannot be empty.")

    try:
        # Store the user's question in the vector store
        store_message(question, "human")

        # Retrieve relevant messages from the vector store
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

        # Check if the question is related to dummy data
        if is_related_to_dummy_data(question):
            # Use optimized semantic search instead of loading all data
            input_data["data"] = search_sales_rep_data(question)

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

        # Use the llm_chain directly instead of chain_with_message_history
        response = llm_chain.invoke(input_data)

        # Ensure response is a string
        if hasattr(response, "content"):
            response = response.content  # Extract content if it's AIMessage
        elif not isinstance(response, str):
            response = json.dumps(response)  # Convert to string if it's not

        # Store the AI's response in the vector store
        store_message(response, "ai")

        return {"answer": response}
    except Exception as e:
        logging.error(f"OpenAI API error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process the AI request. Please try again later.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



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
    temperature=0.7
)

# Load system instruction from assistant.txt
def load_system_instruction():
    with open("assistant.txt", "r") as f:
        return f.read().strip()

# Create a LangChain PromptTemplate
system_instruction = load_system_instruction()
prompt_template = PromptTemplate(
    input_variables=["question", "data"],
    template=(
        "{system_instruction}\n\n"
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

@app.get("/api/sales-reps", summary="Get Sales Representatives", tags=["Sales Reps"])
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

@app.post("/api/ai", summary="AI Question Answering", tags=["AI"])
async def ai_endpoint(request: AIRequest):
    """
    Handles AI-powered question-answering requests.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="The 'question' field cannot be empty.")

    try:
        # Check if the question is related to dummy data
        if is_related_to_dummy_data(question):
            sales_reps = DUMMY_DATA.get("salesReps", [])
            if not sales_reps:
                return {"answer": "I couldn't find any sales representatives in the dummy data."}

            # Check for specific sales rep
            for rep in sales_reps:
                if rep.get("name").lower() in question.lower():
                    # Generate response using the chain
                    response = llm_chain.invoke({
                        "question": question,
                        "data": json.dumps(rep),
                        "system_instruction": system_instruction
                    })
                    return {"answer": response}

            # General response for all sales reps
            response = llm_chain.invoke({
                "question": question,
                "data": json.dumps(sales_reps),
                "system_instruction": system_instruction
            })
            return {"answer": response}
        else:
            # General AI response
            response = llm_chain.invoke({
                "question": question,
                "data": "No specific data available.",
                "system_instruction": system_instruction
            })
            return {"answer": response}
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the AI request. Please try again later.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

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

# Load environment variables
load_dotenv()

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

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment variables.")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler("error.log"),  # Logs to a file
    ],
)

# Load system instruction from a file
def load_system_instruction():
    with open("assistant.txt", "r") as f:
        return f.read().strip()

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

@app.get("/api/sales-reps", summary="Get Sales Representatives", tags=["Sales Reps"])
def get_sales_reps():
    """
    Returns a list of sales representatives from the dummy data.

    **Response:**
    - `200 OK`: A JSON object containing sales representatives and their details.
    """
    return DUMMY_DATA

# Define a Pydantic model for the request body
class AIRequest(BaseModel):
    question: str

@app.post("/api/ai", summary="AI Question Answering", tags=["AI"])
async def ai_endpoint(request: AIRequest):
    """
    Handles AI question-answering requests.

    **Request Body:**
    - `question` (str): The question to be answered.

    **Response:**
    - `200 OK`: A JSON object containing the AI-generated answer.
    - `400 Bad Request`: If the `question` field is missing or invalid.
    - `500 Internal Server Error`: If an error occurs while processing the request.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="The 'question' field cannot be empty.")

    try:
        # Check if the question is related to dummy data
        if is_related_to_dummy_data(question):
            system_instruction = load_system_instruction()
            sales_reps = DUMMY_DATA.get("salesReps", [])
            if not sales_reps:
                return {"answer": "I couldn't find any sales representatives in the dummy data."}

            # Check for specific sales rep
            for rep in sales_reps:
                if rep.get("name").lower() in question.lower():
                    gpt_prompt = (
                        f"The user asked: {question}. Here is the sales representative data for {rep.get('name')}: {json.dumps(rep)}. "
                        f"Please provide a clean, human-readable, and elaborated response."
                    )
                    gpt_response = openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": gpt_prompt},
                        ],
                        max_tokens=2000,
                        temperature=0.7,
                    )
                    return {"answer": gpt_response.choices[0].message.content.strip()}

            # General response for all sales reps
            gpt_prompt = (
                f"The user asked: {question}. Here is the sales representative data: {json.dumps(sales_reps)}. "
                f"Please provide a clean, human-readable, and elaborated response."
            )
            gpt_response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": gpt_prompt},
                ],
                max_tokens=2000,
                temperature=0.7,
            )
            return {"answer": gpt_response.choices[0].message.content.strip()}
        else:
            # General AI response
            system_instruction = load_system_instruction()
            gpt_response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": question},
                ],
                max_tokens=2000,
                temperature=0.7,
            )
            return {"answer": gpt_response.choices[0].message.content.strip()}
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the AI request. Please try again later.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

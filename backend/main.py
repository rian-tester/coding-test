from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import logging

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

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

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.ERROR)

@app.get("/api/sales-reps")
def get_sales_reps():
    """
    Returns a list of sales representatives from the dummy data.
    """
    return DUMMY_DATA

@app.post("/api/ai")
async def ai_endpoint(request: Request):
    """
    Handles AI question-answering requests.
    """
    data = await request.json()
    question = data.get("question", "")
    if not question:
        return {"error": "Question is required"}

    try:
        # Call OpenAI ChatCompletion API
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Use GPT-4o model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        return {"answer": answer}
    except Exception as e:
        logging.error(f"Error processing AI request: {e}")
        return {"answer": "Sorry, I couldn't process your request."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

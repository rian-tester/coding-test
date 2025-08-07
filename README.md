
# Fitra Portofolio


## Introduction

Welcome to my personal portfolio project! This application is designed to showcase my skills as a full-stack developer, with a focus on:

- **Backend:** Python, FastAPI, Retrieval Augmented Generation (RAG), and OpenAI API extensions
- **Frontend:** Node.js, Next.js, GPT-style bubble chat, data visualization, modern web design, and robust API handling

This project demonstrates my ability to build scalable, interactive, and visually appealing web applications. The backend leverages advanced AI and RAG techniques, while the frontend delivers a clean, engaging user experience inspired by modern chat and dashboard interfaces.

In the future, I plan to extend this portfolio to include my skills in CI/CD, containerization, and deployment. Deployment options are still under consideration.

---


---

## Setup & Installation



### Manual Setup

Do this at least once in the first time to run the project:

#### Backend Setup

1. Copy the `.env` file in the **root of the `backend` folder**  
   This is required for the AI API to work.

    - The `.env` file contains the OpenAI API key created specifically for this project.
    - It can be found in the email I sent you along with the repository link.
    - The key will be deleted after **two weeks** from submission, making it safe for temporary use.


2. Navigate to the `backend` directory  
3. Create and activate a virtual environment (required), name of virtual environtment should be **`venv`**:

    ```bash
    cd backend
    python -m venv venv
    
    ```
    When succeded activate the virtual environtment :
    ```bash
    venv\Scripts\activate
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```


5. Start the backend server:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

    ```
6. My python version **Python 3.13.3**

#### Frontend Setup

1. Navigate to the `frontend` directory  
2. Install dependencies:

    ```bash
    npm install
    ```

3. Start the frontend server:

    ```bash
    npm run dev
    ```

4. Open your browser and go to:  
   [http://localhost:3000](http://localhost:3000)

5. My node version **Node.js v20.10.0**
---

### One-Click Setup  

For convenience, I've created a one-click setup option, this can be used later when you need to run both server quickly.

1. After completing the steps above, run the `setup.bat` file in the root directory to launch both servers. 

2. Make sure both servers are running and complete setup by checking the terminal output.  
  Then open localhost in your browser:
   - Frontend Home: [http://localhost:3000](http://localhost:3000)  
   - Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---
## Features & Functionality

### User Interface

- **Interactive Title Animation**: Animated title bar with bounce effects  
- **Dynamic Sidebar**: Collapsible sidebar for better screen real estate management  
- **Responsive Design**: Works on both desktop and mobile devices  
- **Loading States**: Custom spinner for visual feedback during loading  
- **Particle Background**: Interactive background that responds to mouse movement

### Data Visualization

- **Sales Rep Cards**: Clean display of sales representative information  
- **Nested Data Rendering**: Proper handling of nested JSON structures  
- **Color-Coded Deals**:  
  - Green for **closed-won**  
  - Orange for **in-progress**  
  - Red for **closed-lost**  
- **Image Integration**: Profile images for each sales representative

### AI Integration

- **OpenAI Integration**: GPT-4o model for intelligent responses  
- **Database-Aware AI**: Contextual responses using sales rep data  
- **Markdown Support**: Formatted AI responses  
- **Chat Bubble UI**: User-friendly question-answer chat interface  
- **Error Handling**: Graceful fallback when AI request fails

### Additional Features

- **Audio Player**: Background audio with localStorage-persistent settings  
- **Dark Theme**: Modern, eye-friendly dark mode  
- **Gradient Accents**: Stylish buttons and UI elements

---

## Technical Implementation

### Frontend Architecture

- **Component Modularity**: Clean, reusable components  
- **CSS Modules**: Scoped styling to prevent conflicts  
- **State Management**: React hooks for efficient state handling  
- **Async Operations**: Proper data fetching practices  
- **Conditional Rendering**: UI adapts to app state

### Backend Architecture

- **RESTful API**: Well-structured and predictable endpoints  
- **OpenAI Integration**: Smart response strategies  
- **Static File Serving**: Efficient delivery of assets  
- **Error Handling**: Comprehensive with logging  
- **CORS Configuration**: Proper setup for frontend-backend interaction

---

## Testing

- **Unit Tests**: Coverage for backend API endpoints  
- **Error Simulation**: Edge-case testing  
- **Test Documentation**: Well-structured and clear test design

---

## Additional Notes

### API Documentation

The FastAPI backend includes built-in docs:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)  
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Version Control Approach

- Feature branches for isolated development
- Clean history using rebase and cherry-pick, I did rebase because accidentally commit my env file.
- Descriptive and consistent commit messages

---

## What to Try

When testing the application, I recommend:

- Explore the **sales rep cards** and observe **color-coded deal statuses**
- Toggle the **sidebar**
- Switch between **Dummy Data** and **AI Section**
- Ask questions in the **AI Section**, use keyword like : "sales reps", "sales representatives", "dummy data", "sales team", "salesperson", "sales rep", "sales executive", "sales manager"
- Enable **background audio**
- Resize your browser to test **responsiveness**
- Run backend unit tests using:

    ```bash
    cd backend
    pytest
    ```

---

Thank you for reviewing my submission!  
I look forward to discussing my implementation choices and technical decisions.

---

# Updates (LangChain Branch)

In this update, I've significantly enhanced the AI capabilities of the application by integrating **LangChain** and implementing **memory features** for more intelligent, context-aware responses.

---

### 🆕 What's New?

#### Architecture Improvements

- **LangChain Integration**  
  Refactored the backend from direct OpenAI API calls to LangChain's more modular and flexible framework.

- **Vector-Based Memory (RAG)**  
  Implemented **Retrieval Augmented Generation** using `sentence-transformers` and **FAISS** for efficient long-term memory and conversation history.

- **Token Optimization**  
  Introduced intelligent token counting and management to avoid hitting API token limits.

- **Enhanced Context Awareness**  
  The AI now maintains session memory and references past interactions, while still accessing sales rep data when relevant.

---

### 📈 Development Journey

- Started with **direct OpenAI API integration** for basic Q&A functionality  
- Experimented with **LangChain's RunnableWithMessageHistory** for session memory  
- Encountered **token limit issues** using plain conversation history  
- Shifted to **vector-based retrieval (RAG)** using `sentence-transformers` for memory optimization  
- Fine-tuned history retrieval to ensure **only the most relevant messages are used**

---

### ⚙️ Technical Implementation

- Used `sentence-transformers` to generate **embeddings** for user-AI interactions  
- Implemented a **FAISS vector store** for fast similarity search  
- Maintained full compatibility with existing **dummy sales rep data integration**  
- Optimized token usage with intelligent trimming and batching

---

### 🚀 How to Use This Branch

1. **Switch to the `LangChain` branch**:

    ```bash
    git checkout langchain
    ```

2. **Reinstall backend requirements** (new dependencies added):

    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3. **Start both servers** as usual

    ```bash
    # Backend
    uvicorn main:app --reload

    # Frontend (in separate terminal)
    cd frontend
    npm run dev
    ```

> ⚠️ **Note:** This feature only works with the latest commit on the `langchain` branch. Make sure you're using the most recent version.

---

### 🧠 Testing the Memory Feature

You can now test the AI's ability to **remember past conversations**:

- Start by saying:

    ```
    My name is [your name]
    ```

- Then later ask:

    ```
    What's my name?
    ```

The AI should recall your name correctly based on previous context.  
You can also continue using **sales rep data** keywords and the AI will maintain context intelligently across turns.

---


# Fitra Portofolio


## Introduction

Welcome to my personal portfolio project! This application is designed to showcase my skills as a full-stack developer, with a focus on:

- **Backend:** Python, FastAPI, Retrieval Augmented Generation (RAG), and OpenAI API extensions
- **Frontend:** Node.js, Next.js, GPT-style bubble chat, data visualization, modern web design, and robust API handling

This project demonstrates my ability to build scalable, interactive, and visually appealing web applications. The backend leverages advanced AI and RAG techniques, while the frontend delivers a clean, engaging user experience inspired by modern chat and dashboard interfaces.

In the future, I plan to extend this portfolio to include my skills in CI/CD, containerization, and deployment. Deployment options are still under consideration.

---

## Project Evolution & Technical Progression

### Backend Evolution

#### Phase 1: Basic Implementation
Initially, the backend started with a simple approach:
- **Basic RAG Implementation**: Manual keyword matching and simple OpenAI API calls
- **Hardcoded Routing**: Direct conditional logic to determine whether a question was sales-related or general
- **Limited Context Awareness**: No memory or conversation history

#### Phase 2: Advanced AI Routing
The backend evolved to implement sophisticated AI-powered routing:
- **Intelligent Question Classification**: Replaced manual keyword matching with AI-powered analysis using GPT models
- **Dynamic Routing System**: Implemented `AIRouter` service that intelligently categorizes questions as sales or general queries
- **Confidence-Based Decision Making**: Added confidence scoring to ensure accurate routing decisions
- **Modular Architecture**: Separated concerns into distinct services (`AIRouter`, `RAGService`, `ChatService`, `DataService`)

#### Phase 3: Enhanced RAG & Memory
Current implementation features:
- **Advanced RAG Pipeline**: Sophisticated retrieval-augmented generation with context-aware responses
- **Conversation Memory**: Session-based memory management for contextual conversations
- **Performance Optimization**: Comprehensive logging and timing analysis for request optimization
- **Error Handling**: Robust error management with graceful fallbacks
- **API Documentation**: Complete Swagger/OpenAPI documentation with detailed examples

### Frontend Evolution

#### Phase 1: Basic Sales Dashboard (V1)
The initial frontend was a simple data display:
- Basic sales representative cards layout
- Simple data fetching and display
- Minimal styling and basic responsiveness

**Sales Dashboard V1:**
![Sales Dashboard V1](./Readme/Fitra%20portfolio%20V1%20sales.png)

**Chat Section V1:**
![Chat Section V1](./Readme/Fitra%20portfolio%20V1%20Chat.png)

#### Phase 2: Modern UI Transformation (V2)
Complete frontend style revamp with enhanced user experience:
- **Elegant Design System**: Transformed from basic dashboard to modern, elegant interface
- **Simplified Layout**: Clean, minimalist design focusing on usability and visual hierarchy
- **Advanced Styling**: Professional gradient backgrounds, smooth animations, and modern typography
- **Theme Integration**: Consistent themes with carefully chosen color palettes
- **Modern Dashboard Layout**: Completely refactored dashboard with improved visual organization
- **Brand New Chat Interface**: Redesigned chat section with bubble-style conversations and markdown support
- **Intelligent Frontend-Backend Integration**: Updated frontend logic to seamlessly work with new AI routing system
- **Real-time Statistics**: Dynamic stats and information pulled directly from backend APIs
- **Interactive Components**: New circular button designs and intuitive navigation elements
- **Responsive Architecture**: Mobile-first design ensuring perfect functionality across all device sizes

**Sales Dashboard V2:**
![Sales Dashboard V2 - Part 1](./Readme/Fitra%20portfolio%20V2%20sales%20part%201.png)
![Sales Dashboard V2 - Part 2](./Readme/fitra%20portfolio%20V2%20sales%20part%202.png)

**Chat Section V2:**
![Chat Section V2 - Part 1](./Readme/Fitra%20portfolio%20V2%20char%20part%201.png)
![Chat Section V2 - Part 2](./Readme/Fitra%20portfolio%20V2%20chat%20part%202.png)

### Technical Implementation Details

#### Backend Architecture
- **Microservice-Like Structure**: Cleanly separated services for different functionalities
- **Advanced AI Integration**: Multiple AI strategies (RAG, general chat, routing) working in harmony
- **Performance Monitoring**: Request-level timing and performance analytics
- **Scalable Design**: Built with expansion and additional features in mind

#### Frontend Architecture
- **Component-Based Design**: Modular React components for maintainability
- **State Management**: Efficient state handling with React hooks
- **CSS Modules**: Scoped styling preventing conflicts and ensuring maintainability
- **Modern Web Standards**: ES6+, responsive design, and progressive enhancement

---


---

## Setup & Installation



### Manual Setup

Do this at least once in the first time to run the project:

#### Backend Setup

1. **Setup OpenAI API Key** in the **root of the `backend` folder**  
   Create a `.env` file with your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   **For Visitors/Users:**
   - Please provide your own OpenAI API key and add it to the `.env` file with the variable name `OPENAI_API_KEY=`

   **For Interviewers:**
   - If you are an interviewer and need a temporary API key for testing, please email me at: **fitransyah.rusman@gmail.com**


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
- **Theme Selector**: Interactive theme switching with multiple color schemes and visual options
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

Thank you for reviewing my portfolio!  
I look forward to discussing my implementation choices and technical decisions.

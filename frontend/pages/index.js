import { useState, useEffect } from "react";
import Head from "next/head";
import Background from "../components/Background";
import Sidebar from "../components/Sidebar"; // Import the Sidebar component
import RepCard from "../components/RepCard"; // Import the RepCard component
import Spinner from "../components/Spinner"; // Import the Spinner component
import ChatBot from "../components/ChatBot"; // Import the ChatBot component

export default function Home() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingAI, setLoadingAI] = useState(false); // New state for AI loading
  const [question, setQuestion] = useState("");
  const [answerHistory, setAnswerHistory] = useState([]); // Store history of questions and answers
  const [activeSection, setActiveSection] = useState("dummy-data"); // Default section
  const [isDocked, setIsDocked] = useState(false); // Sidebar docking state

  useEffect(() => {
    setTimeout(() => {
      fetch("http://localhost:8000/api/sales-reps")
        .then((res) => res.json())
        .then((data) => {
          setUsers(data.salesReps || []);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Failed to fetch data:", err);
          setLoading(false);
        });
    }, 750); // Simulate a 2-second delay
  }, []);

  const handleAskQuestion = async () => {
    if (question.trim() === "") return; // Prevent submitting empty or whitespace-only questions
    setLoadingAI(true); // Start spinner
    try {
      const response = await fetch("http://localhost:8000/api/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      console.log("AI Response:", data); // Debugging log

      if (data.answer) {
        // Add the question and answer to the history
        setAnswerHistory((prevHistory) => [
          { question, answer: data.answer },
          ...prevHistory, // Add newest chat at the top
        ]);
      } else {
        console.error("No answer field in response:", data);
      }
      setQuestion(""); // Clear the text box after submission
    } catch (error) {
      console.error("Error in AI request:", error);
    } finally {
      setLoadingAI(false); // Stop spinner
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey && question.trim() !== "") {
      e.preventDefault(); // Prevent default Enter behavior
      handleAskQuestion(); // Submit the question when Enter is pressed
    }
  };

  const handleClearChat = () => {
    setAnswerHistory([]); // Clear the chat history
    setQuestion(""); // Clear the input field
  };

  const handleNavigate = (section) => {
    setActiveSection(section); // Update the active section
  };

  const handleToggleDock = () => {
    setIsDocked(!isDocked); // Toggle the docking state
  };

  return (
    <>
      <Head/>
      {/* Background Visualization */}
      <Background/>

      <div className="layout">
        {/* Title Bar */}
        <div className="title-bar">
          <h1>Next.js + FastAPI Sample</h1>
        </div>

        {/* Sidebar and Main Content */}
        <div className="content-wrapper">
          {/* Sidebar */}
          <Sidebar
            isDocked={isDocked}
            onToggleDock={handleToggleDock}
            onNavigate={handleNavigate}
          />

          {/* Main Content */}
          <div className={`main-content ${isDocked ? "expanded" : ""}`}>
            {/* Content Based on Active Section */}
            {activeSection === "dummy-data" && (
              <section className="dummy-data">
                <h2 className="section-header blue">Dummy Data</h2>
                {loading ? (
                  <Spinner /> // Use the Spinner component here
                ) : (
                  <ul>
                    {users.map((rep) => (
                      <RepCard key={rep.id} rep={rep} /> // Use the RepCard component
                    ))}
                  </ul>
                )}
              </section>
            )}

            {activeSection === "ai-section" && (
              <section className="ai-section">
                <h2 className="section-header blue">Ask a Question</h2>
                <ChatBot
                  question={question}
                  setQuestion={setQuestion}
                  answerHistory={answerHistory}
                  loadingAI={loadingAI}
                  handleAskQuestion={handleAskQuestion}
                  handleClearChat={handleClearChat}
                  handleKeyDown={handleKeyDown}
                />
              </section>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
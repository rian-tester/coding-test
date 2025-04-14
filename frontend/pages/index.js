import { useState, useEffect } from "react";
import Head from "next/head";
import Background from "../components/Background";
import Sidebar from "../components/Sidebar";
import ReactMarkdown from "react-markdown";
import RepCard from "../components/RepCard"; // Import the RepCard component
import Spinner from "../components/Spinner"; // Import the Spinner component

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
                <div className="chat-container">
                  <div className="input-container">
                    <textarea
                      placeholder="Shift + Enter for new line"
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      onKeyDown={handleKeyDown}
                      className="question-textbox"
                      disabled={loadingAI} // Disable input while loading
                    />
                    <div className="button-container">
                      <button
                        onClick={handleClearChat}
                        className="clear-button"
                        disabled={loadingAI} // Disable clear button while loading
                      >
                        Clear
                      </button>
                      <button
                        onClick={handleAskQuestion}
                        className="ask-button"
                        disabled={loadingAI} // Disable ask button while loading
                      >
                        Ask
                      </button>
                    </div>
                  </div>

                  {/* Show Spinner While Waiting for AI Response */}
                  {loadingAI ? (
                    <Spinner /> // Use Spinner for AI loading
                  ) : (
                    <div className="response-history">
                      {answerHistory.map((item, index) => (
                        <div key={index} className="response-item">
                          <div className="bubble user-bubble">
                            <strong>Question:</strong> {item.question}
                          </div>
                          <div className="bubble ai-bubble">
                            <strong>AI Response:</strong>
                            <ReactMarkdown>{item.answer}</ReactMarkdown>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </section>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
import { useState, useEffect } from "react";
import Head from "next/head";
import Background from "../components/_background";
import Sidebar from "../components/Sidebar";

export default function Home() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [activeSection, setActiveSection] = useState("dummy-data"); // Default section
  const [isDocked, setIsDocked] = useState(false); // Sidebar docking state

  useEffect(() => {
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
  }, []);

  const handleAskQuestion = async () => {
    if (question.trim() === "") return; // Prevent submitting empty or whitespace-only questions
    try {
      const response = await fetch("http://localhost:8000/api/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      setAnswer(data.answer); // Update the answer
      setQuestion(""); // Clear the text box after submission
    } catch (error) {
      console.error("Error in AI request:", error);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && question.trim() !== "") {
      handleAskQuestion(); // Submit the question when Enter is pressed
    }
  };

  const handleNavigate = (section) => {
    setActiveSection(section); // Update the active section
  };

  const handleToggleDock = () => {
    setIsDocked(!isDocked); // Toggle the docking state
  };

  return (
    <>
      <Head>
        <link
          href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap"
          rel="stylesheet"
        />
      </Head>

      {/* Background Visualization */}
      <Background />

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
                  <p>Loading...</p>
                ) : (
                  <ul>
                    {users.map((rep) => (
                      <li key={rep.id} className="rep-card">
                        <div className="rep-header">
                          <strong>{rep.name}</strong> - {rep.role}
                        </div>
                        <hr className="divider" />
                        <div className="rep-content">
                          <div className="rep-image">
                            <img
                              src={`http://localhost:8000/images/${rep.name}.webp`}
                              alt={rep.name}
                              className="sales-image"
                            />
                          </div>
                          <div className="rep-details">
                            <ul>
                              <li>Skills: {rep.skills.join(", ")}</li>
                              <li>
                                Deals:
                                <ul>
                                  {rep.deals.map((deal, index) => (
                                    <li key={index}>
                                      {deal.client} - ${deal.value} ({deal.status})
                                    </li>
                                  ))}
                                </ul>
                              </li>
                            </ul>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            )}

            {activeSection === "ai-section" && (
              <section className="ai-section">
                <h2 className="section-header blue">Ask a Question</h2>
                <div className="question-container">
                  <textarea
                    placeholder="Shift + Enter for new line"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault(); // Prevent default Enter behavior
                        handleAskQuestion(); // Submit the question
                      }
                    }}
                    className="question-textbox"
                  />
                </div>
                <div className="button-container">
                  <button
                    onClick={() => {
                      setAnswer(""); // Remove the displayed answer
                      setQuestion(""); // Clear the text box
                    }}
                    className="clear-button"
                  >
                    Clear
                  </button>
                  <button onClick={handleAskQuestion} className="ask-button">
                    Ask
                  </button>
                </div>
                {answer && (
                  <div className="response">
                    <strong>AI Response:</strong> {answer}
                  </div>
                )}
              </section>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
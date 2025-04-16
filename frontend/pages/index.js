import { useState, useEffect } from "react";
import Head from "next/head";
import Background from "../components/Background";
import Sidebar from "../components/Sidebar";
import RepCard from "../components/RepCard";
import Spinner from "../components/Spinner";
import ChatBot from "../components/ChatBot";
import AudioPlayer from "../components/AudioPlayer"; // Import the new AudioPlayer component

export default function Home() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingAI, setLoadingAI] = useState(false);
  const [question, setQuestion] = useState("");
  const [answerHistory, setAnswerHistory] = useState([]);
  const [activeSection, setActiveSection] = useState("dummy-data");
  const [isDocked, setIsDocked] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(false); // Default to false

  // Initialize soundEnabled from localStorage on the client side
  useEffect(() => {
    const storedSoundSetting = localStorage.getItem("soundEnabled");
    if (storedSoundSetting !== null) {
      setSoundEnabled(JSON.parse(storedSoundSetting));
    }
  }, []);

  // Fetch data for dummy-data section
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
    }, 750);
  }, []);

  // Handle navigation to different sections
  const handleNavigate = (section) => {
    setActiveSection(section);
  };

  // Handle toggling the sidebar docked state
  const handleToggleDock = () => {
    setIsDocked(!isDocked);
  };

  // AI Section functionality
  const handleAskQuestion = async () => {
    if (question.trim() === "") return;
    setLoadingAI(true);
    try {
      const headers = {
        "Content-Type": "application/json",
        "X-Session-ID": "unique-session-id", // Generate or retrieve a session ID
      };

      const response = await fetch("http://localhost:8000/api/ai", {
        method: "POST",
        headers,
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      console.log("AI Response:", data);

      if (data.answer) {
        setAnswerHistory((prevHistory) => [
          { question, answer: data.answer },
          ...prevHistory,
        ]);
      } else {
        console.error("No answer field in response:", data);
      }
      setQuestion("");
    } catch (error) {
      console.error("Error in AI request:", error);
    } finally {
      setLoadingAI(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey && question.trim() !== "") {
      e.preventDefault();
      handleAskQuestion();
    }
  };

  const handleClearChat = () => {
    setAnswerHistory([]);
    setQuestion("");
  };


  return (
    <>
      <Head />
      <Background />

      <div className="layout">
        <div className="title-bar">
          <h1>InterOpera Coding Test</h1>
        </div>

        <div className="content-wrapper">
          <Sidebar
            isDocked={isDocked}
            onToggleDock={handleToggleDock}
            onNavigate={handleNavigate}
          />

          <main className={`main-content ${isDocked ? "expanded" : ""}`}>
            {/* Dummy Data Section */}
            {activeSection === "dummy-data" && (
              <div className="dummy-section-wrapper">
                <h2 className="section-header blue">Dummy Data</h2>
                {loading ? (
                  <Spinner />
                ) : (
                  <ul>
                    {users.map((rep) => (
                      <RepCard key={rep.id} rep={rep} />
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* AI Section */}
            {activeSection === "ai-section" && (
              <div className="ai-section-wrapper">
                <h2 className="section-header blue">Ask a Question</h2>
                <div style={{ height: "100%", minHeight: 0, display: "flex", flexDirection: "column" }}>
                  <ChatBot
                    question={question}
                    setQuestion={setQuestion}
                    answerHistory={answerHistory}
                    loadingAI={loadingAI}
                    handleAskQuestion={handleAskQuestion}
                    handleClearChat={handleClearChat}
                    handleKeyDown={handleKeyDown}
                  />
                </div>
              </div>
            )}
          </main>
        </div>

        {/* Audio Player Component */}
        <AudioPlayer
          soundEnabled={soundEnabled}
          setSoundEnabled={setSoundEnabled}
        />
      </div>
    </>
  );
}
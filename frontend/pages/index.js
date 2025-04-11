import { useState, useEffect } from "react";
import Head from "next/head";
import Background from "../components/_background";

export default function Home() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [showDummyData, setShowDummyData] = useState(true);
  const [showAISection, setShowAISection] = useState(true);

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
    try {
      const response = await fetch("http://localhost:8000/api/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      setAnswer(data.answer);
    } catch (error) {
      console.error("Error in AI request:", error);
    }
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

      <div className="container">
        {/* Title Bar */}
        <div className="title-bar">
          <h1>Next.js + FastAPI Sample</h1>
        </div>

        {/* Dummy Data Section */}
        <section className="dummy-data">
          <h2
            onClick={() => setShowDummyData(!showDummyData)}
            className={`section-header blue`}
          >
            Dummy Data {showDummyData ? "▼" : "▶"}
          </h2>
          {showDummyData && (
            <>
              {loading ? (
                <p>Loading...</p>
              ) : (
                <ul>
                  {users.map((rep) => (
                    <li key={rep.id} className="rep-card">
                      {/* Name and Role */}
                      <div className="rep-header">
                        <strong>{rep.name}</strong> - {rep.role}
                      </div>
                      <hr className="divider" />
                      {/* Horizontal Layout */}
                      <div className="rep-content">
                        {/* Image Section */}
                        <div className="rep-image">
                          <img
                            src={`http://localhost:8000/images/${rep.name}.webp`}
                            alt={rep.name}
                            className="sales-image"
                          />
                        </div>
                        {/* Details Section */}
                        <div className="rep-details">
                          <ul>
                            <li>
                              Skills:
                              <ul>
                                {rep.skills.map((skill, index) => (
                                  <li key={index}>- {skill}</li>
                                ))}
                              </ul>
                            </li>
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
            </>
          )}
        </section>

        {/* AI Section */}
        <section className="ai-section">
          <h2
            onClick={() => setShowAISection(!showAISection)}
            className={`section-header green`}
          >
            Ask a Question {showAISection ? "▼" : "▶"}
          </h2>
          {showAISection && (
            <div>
              <input
                type="text"
                placeholder="Enter your question..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              />
              <button onClick={handleAskQuestion}>Ask</button>
              {answer && (
                <div className="response">
                  <strong>AI Response:</strong> {answer}
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </>
  );
}
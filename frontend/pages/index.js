import { useState, useEffect } from "react";

export default function Home() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [showDummyData, setShowDummyData] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/sales-reps")
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched data:", data); // Debug log
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
    <div style={{ padding: "2rem" }}>
      {/* Main Content */}
      <div>
        {/* Title Bar */}
        <div>
          <h1>Next.js + FastAPI Sample</h1>
        </div>

        {/* Dummy Data Section */}
        <section>
          <h2>Dummy Data </h2>
          {showDummyData && (
            <>
              {loading ? (
                <p>Loading...</p>
              ) : (
                <ul>
                  {users.map((rep) => (
                    <li key={rep.id}>
                      
                      {/* Person's Details */}
                      <div>
                        <strong>{rep.name}</strong> - {rep.role} ({rep.region})
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
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </section>
      </div>

      <section>
        <h2>Ask a Question (AI Endpoint)</h2>
        <div>
          <input
            type="text"
            placeholder="Enter your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button onClick={handleAskQuestion}>Ask</button>
        </div>
        {answer && (
          <div style={{ marginTop: "1rem" }}>
            <strong>AI Response:</strong> {answer}
          </div>
        )}
      </section>
    </div>
  );
}

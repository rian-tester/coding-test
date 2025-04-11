import { useState, useEffect } from "react";
import Head from "next/head";

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
      <div className="p-8 bg-gray-800 text-white rounded-lg shadow-lg">
        {/* Title Bar */}
        <div className="sticky top-0 z-10 bg-gradient-to-r from-blue-500 to-green-500 p-4 rounded-lg shadow-md text-center">
          <h1 className="text-3xl font-bold">Next.js + FastAPI Sample</h1>
        </div>

        {/* Dummy Data Section */}
        <section className="mt-8">
          <h2
            onClick={() => setShowDummyData(!showDummyData)}
            className="cursor-pointer text-xl font-semibold text-blue-400 mb-4"
          >
            Dummy Data {showDummyData ? "▼" : "▶"}
          </h2>
          {showDummyData && (
            <>
              {loading ? (
                <p>Loading...</p>
              ) : (
                <ul className="space-y-4">
                  {users.map((rep) => (
                    <li
                      key={rep.id}
                      className="p-4 bg-gray-700 rounded-lg shadow-md"
                    >
                      <div>
                        <strong>{rep.name}</strong> - {rep.role} ({rep.region})
                        <ul className="mt-2">
                          <li>Skills: {rep.skills.join(", ")}</li>
                          <li>
                            Deals:
                            <ul className="ml-4 list-disc">
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

        {/* AI Section */}
        <section className="mt-8">
          <h2
            onClick={() => setShowAISection(!showAISection)}
            className="cursor-pointer text-xl font-semibold text-green-400 mb-4"
          >
            Ask a Question {showAISection ? "▼" : "▶"}
          </h2>
          {showAISection && (
            <div className="p-4 bg-gray-700 rounded-lg shadow-md">
              <input
                type="text"
                placeholder="Enter your question..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="p-2 rounded border border-gray-300 mr-2"
              />
              <button
                onClick={handleAskQuestion}
                className="px-4 py-2 bg-gradient-to-r from-blue-500 to-green-500 text-white rounded shadow"
              >
                Ask
              </button>
              {answer && (
                <div className="mt-4 p-4 bg-gray-600 rounded">
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

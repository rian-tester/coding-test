import React from "react";
import ReactMarkdown from "react-markdown";
import Spinner from "./Spinner";
import styles from "./styles/ChatBot.module.css";

export default function ChatBot({
  question,
  setQuestion,
  answerHistory,
  loadingAI,
  handleAskQuestion,
  handleClearChat,
  handleKeyDown,
}) {
  return (
    <>
      {/* We'll leave the section with h2 in the index.js */}
      <div className={styles["chat-container"]}>
        <div className={styles["input-container"]}>
          <textarea
            placeholder="Shift + Enter for new line"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            className={styles["question-textbox"]}
            disabled={loadingAI}
          />
          <div className={styles["button-container"]}>
            <button
              onClick={handleClearChat}
              className={styles["clear-button"]}
              disabled={loadingAI}
            >
              Clear
            </button>
            <button
              onClick={handleAskQuestion}
              className={styles["ask-button"]}
              disabled={loadingAI}
            >
              Ask
            </button>
          </div>
        </div>

        {/* Show Spinner While Waiting for AI Response */}
        {loadingAI ? (
          <Spinner /> 
        ) : (
          <div className={styles["response-history"]}>
            {answerHistory.map((item, index) => (
              <div key={index} className={styles["response-item"]}>
                <div className={`${styles.bubble} ${styles["user-bubble"]}`}>
                  <strong>Question:</strong> {item.question}
                </div>
                <div className={`${styles.bubble} ${styles["ai-bubble"]}`}>
                  <strong>AI Response:</strong>
                  <ReactMarkdown>{item.answer}</ReactMarkdown>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
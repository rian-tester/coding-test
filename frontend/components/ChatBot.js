import React, { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import Spinner from "./Spinner";
import styles from "./styles/ChatBot.module.css";

function preprocessMarkdown(content) {
  return content.replace(/\n\n(\d+\.)/g, "\n$1");
}

function MarkdownRenderer({ content }) {
  return <ReactMarkdown>{content}</ReactMarkdown>;
}

export default function ChatBot({
  question,
  setQuestion,
  answerHistory,
  loadingAI,
  handleAskQuestion,
  handleClearChat,
  handleKeyDown,
}) {
  const responseContainerRef = useRef(null);

  // Scroll to the bottom whenever answerHistory changes
  useEffect(() => {
    if (responseContainerRef.current) {
      responseContainerRef.current.scrollTop = responseContainerRef.current.scrollHeight;
    }
  }, [answerHistory]);

  return (
    <div className={styles["chat-wrapper"]}>
      {/* Response Container */}
      <div className={styles["response-container"]} ref={responseContainerRef}>
        {loadingAI ? (
          <div className={styles["spinner-container"]}>
            <Spinner />
          </div>
        ) : (
          <div className={styles["response-history"]}>
            {answerHistory.slice().reverse().map((item, index) => (
              <div key={index} className={styles["response-item"]}>
                <div className={`${styles.bubble} ${styles["ai-bubble"]}`}>
                  <strong>AI Response:</strong>
                  <MarkdownRenderer content={preprocessMarkdown(item.answer)} />
                </div>
                <div className={`${styles.bubble} ${styles["user-bubble"]}`}>
                  <strong>Question:</strong>
                  <div className={styles["question-text"]}>{item.question}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Input Container */}
      <div className={styles["input-container"]}>
        <textarea
          placeholder="Type your question here..."
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
    </div>
  );
}
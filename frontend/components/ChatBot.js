import React from "react";
import ReactMarkdown from "react-markdown";
import Spinner from "./Spinner";
import styles from "./styles/ChatBot.module.css";

function preprocessMarkdown(content) {
    // Replace double newlines before numbered list items with a single newline
    return content.replace(/\n\n(\d+\.)/g, '\n$1');
}

function MarkdownRenderer({ content }) {
    if (typeof content !== 'string') {
        console.error('Expected string content for MarkdownRenderer, received:', content);
        content = JSON.stringify(content); // Fallback to string
    }
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
  return (
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
                <MarkdownRenderer content={preprocessMarkdown(item.answer)} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
import React, { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import conversationLogger from "../utils/logger";
import styles from "./styles/ChatBot.module.css";

function preprocessMarkdown(content) {
  return content.replace(/\n\n(\d+\.)/g, "\n$1");
}

function MarkdownRenderer({ content }) {
  return <ReactMarkdown>{content}</ReactMarkdown>;
}

function CircularProgress({ progress, onStop, isProcessing }) {
  // Calculate strokeDashoffset for emptying circle (reverse of filling)
  const radius = 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (circumference * progress) / 100;
  
  return (
    <div className={styles["circular-progress-container"]}>
      <svg className={styles["circular-progress"]} width="24" height="24" viewBox="0 0 24 24">
        <circle
          cx="12"
          cy="12"
          r={radius}
          fill="none"
          stroke="var(--secondary-accent)"
          strokeWidth="2"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className={styles["progress-circle"]}
        />
      </svg>
      {isProcessing && (
        <button
          onClick={onStop}
          className={styles["stop-button"]}
          title="Stop processing"
        >
          <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
            <rect width="10" height="10" />
          </svg>
        </button>
      )}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className={`${styles.message} ${styles["ai-message"]} ${styles["typing-indicator"]}`}>
      <span></span>
      <span></span>
      <span></span>
    </div>
  );
}

export default function ChatBot({
  question,
  setQuestion,
  answerHistory,
  loadingAI,
  addAnswerToHistory,
  handleClearChat,
}) {
  const responseContainerRef = useRef(null);
  const [processingStatus, setProcessingStatus] = useState("");
  const [progress, setProgress] = useState(0);
  const [processingTime, setProcessingTime] = useState(0);
  const [routeInfo, setRouteInfo] = useState("");
  const [showTyping, setShowTyping] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    if (responseContainerRef.current) {
      responseContainerRef.current.scrollTop = responseContainerRef.current.scrollHeight;
    }
  }, [answerHistory]);

  const parseStatusFromResponse = (data) => {
    const routeType = data.route_type || "unknown";
    const processingTime = data.processing_time || 0;
    
    return {
      status: "Complete",
      progress: 100,
      time: processingTime,
      route: routeType
    };
  };

  const simulateProgress = (routeType) => {
    const stages = routeType === "sales" 
      ? [
          { status: "Analyzing question...", progress: 80, delay: 300 },
          { status: "Route decision: sales", progress: 60, delay: 200 },
          { status: "Searching sales data...", progress: 40, delay: 400 },
          { status: "Generating response...", progress: 20, delay: 600 }
        ]
      : [
          { status: "Analyzing question...", progress: 70, delay: 400 },
          { status: "Route decision: general", progress: 50, delay: 300 },
          { status: "Processing general question...", progress: 25, delay: 800 }
        ];

    stages.forEach((stage, index) => {
      setTimeout(() => {
        setProcessingStatus(stage.status);
        setProgress(stage.progress);
        if (stage.status.includes("Route decision:")) {
          setRouteInfo(stage.status.split(": ")[1]);
        }
      }, stage.delay * (index + 1));
    });
  };

  const enhancedHandleAskQuestion = async () => {
    if (question.trim() === "" || isProcessing) return;
    
    setIsProcessing(true);
    setProcessingStatus("Starting...");
    setProgress(100); // Start with full circle
    setProcessingTime(0);
    setRouteInfo("");
    setShowTyping(true);
    
    const currentQuestion = question.trim();
    abortControllerRef.current = new AbortController();
    const startTime = Date.now();
    
    try {
      setProcessingStatus("Analyzing question...");
      setProgress(90); // Gradually decrease
      
      const response = await fetch("http://localhost:8000/api/ai", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: currentQuestion }),
        signal: abortControllerRef.current.signal,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      const endTime = Date.now();
      const totalTime = (endTime - startTime) / 1000;
      
      simulateProgress(data.route_type || "general");
      
      setTimeout(() => {
        const { status, progress: finalProgress, time, route } = parseStatusFromResponse(data);
        setProcessingStatus("Complete");
        setProgress(0); // End with empty circle
        setProcessingTime(totalTime);
        setRouteInfo(route);

        if (data.answer && typeof addAnswerToHistory === 'function') {
          addAnswerToHistory(currentQuestion, data.answer);
          // Log the conversation (non-blocking)
          conversationLogger.logConversation(currentQuestion, data.answer).catch(console.error);
        }
        
        setQuestion("");
        setShowTyping(false);
        setIsProcessing(false);
        
        setTimeout(() => {
          setProcessingStatus("");
          setProgress(0);
          setProcessingTime(0);
          setRouteInfo("");
        }, 3000);
      }, 1200);

    } catch (error) {
      setShowTyping(false);
      setIsProcessing(false);
      
      if (error.name === 'AbortError') {
        setProcessingStatus("Stopped by user");
      } else {
        console.error("Error in AI request:", error);
        setProcessingStatus("Error occurred");
        
        // Log the error
        conversationLogger.logError(error, "AI request failed").catch(console.error);
        
        if (typeof addAnswerToHistory === 'function') {
          addAnswerToHistory(
            currentQuestion, 
            "I apologize, but there was an error processing your request. Please try again."
          );
        }
      }
      
      setQuestion("");
      setTimeout(() => {
        setProcessingStatus("");
        setProgress(0);
        setProcessingTime(0);
        setRouteInfo("");
      }, 2000);
    }
  };

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsProcessing(false);
    setShowTyping(false);
    setProcessingStatus("Stopped by user");
    setTimeout(() => {
      setProcessingStatus("");
      setProgress(0);
      setProcessingTime(0);
      setRouteInfo("");
    }, 2000);
  };

  const enhancedHandleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey && question.trim() !== "" && !isProcessing) {
      e.preventDefault();
      enhancedHandleAskQuestion();
    }
  };

  const enhancedHandleClearChat = async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsProcessing(false);
    setProcessingStatus("");
    setProgress(0);
    setProcessingTime(0);
    setRouteInfo("");
    setShowTyping(false);
    handleClearChat();
  };

  return (
    <div className={styles["chat-container"]}>
      <div className={styles["chat-header"]}>
        <h2>Sales Dashboard Assistant</h2>
        <p>{processingStatus || "Ready when you are."}</p>
        {(processingTime > 0 || routeInfo) && (
          <div className={styles["status-info"]}>
            {processingTime > 0 && <span>⏱️ {processingTime.toFixed(2)}s</span>}
            {routeInfo && <span>🎯 {routeInfo}</span>}
          </div>
        )}
      </div>

      <div className={styles["chat-messages"]} ref={responseContainerRef}>
        {answerHistory.length === 0 && !showTyping && (
          <div className={`${styles.message} ${styles["ai-message"]}`}>
            <p>Hello! How can I help you today?</p>
          </div>
        )}
        
        {answerHistory.slice().reverse().map((item, index) => (
          <React.Fragment key={index}>
            <div className={`${styles.message} ${styles["user-message"]}`}>
              <p>{item.question}</p>
            </div>
            <div className={`${styles.message} ${styles["ai-message"]}`}>
              <MarkdownRenderer content={preprocessMarkdown(item.answer)} />
            </div>
          </React.Fragment>
        ))}
        
        {showTyping && <TypingIndicator />}
      </div>

      {processingStatus && (
        <div className={styles["ai-status-container"]}>
          <p className={styles["ai-status-text"]}>{processingStatus}</p>
        </div>
      )}

      <form 
        className={styles["chat-form"]} 
        onSubmit={(e) => {
          e.preventDefault();
          enhancedHandleAskQuestion();
        }}
      >
        <input
          type="text"
          placeholder="Type your message..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={enhancedHandleKeyDown}
          className={styles["message-input"]}
          disabled={isProcessing}
          autoComplete="off"
        />
        <button
          type="submit"
          className={`${styles["send-button"]} ${isProcessing ? styles.loading : ""}`}
          disabled={(!question.trim() && !isProcessing) || isProcessing}
        >
          {isProcessing ? (
            <CircularProgress 
              progress={progress} 
              onStop={handleStop} 
              isProcessing={true} 
            />
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2 .01 7z"/>
            </svg>
          )}
        </button>
      </form>
    </div>
  );
}

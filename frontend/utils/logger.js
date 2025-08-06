class ConversationLogger {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.sessionStarted = false;
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async initializeSession() {
    if (!this.sessionStarted) {
      try {
        await fetch('/api/log-conversation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'session_start',
            sessionId: this.sessionId,
            timestamp: new Date().toISOString()
          })
        });
        this.sessionStarted = true;
      } catch (error) {
        console.error('Failed to initialize session:', error);
      }
    }
  }

  async logConversation(userQuestion, aiAnswer) {
    try {
      await this.initializeSession();
      
      await fetch('/api/log-conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'conversation',
          sessionId: this.sessionId,
          userQuestion: userQuestion.trim(),
          aiAnswer: aiAnswer.trim(),
          timestamp: new Date().toISOString()
        })
      });
    } catch (error) {
      console.error('Failed to log conversation:', error);
    }
  }

  async logError(error, context = '') {
    try {
      await fetch('/api/log-conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'error',
          sessionId: this.sessionId,
          error: error.toString(),
          context,
          timestamp: new Date().toISOString()
        })
      });
    } catch (logError) {
      console.error('Failed to log error:', logError);
    }
  }
}

const conversationLogger = new ConversationLogger();

export default conversationLogger;

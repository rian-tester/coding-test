import fs from 'fs';
import path from 'path';

const LOG_FILE = path.join(process.cwd(), 'conv-log.txt');

function ensureLogFile() {
  if (!fs.existsSync(LOG_FILE)) {
    const initialContent = `=== Conversation Log Started ===\n`;
    fs.writeFileSync(LOG_FILE, initialContent, 'utf8');
  }
}

function formatTimestamp(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
}

function appendToLog(content) {
  try {
    fs.appendFileSync(LOG_FILE, content, 'utf8');
  } catch (error) {
    console.error('Failed to write to log file:', error);
  }
}

export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    ensureLogFile();

    const { type, sessionId, timestamp, userQuestion, aiAnswer, error, context } = req.body;

    switch (type) {
      case 'session_start':
        const sessionHeader = `\n=== Session Started: ${formatTimestamp(timestamp)} ===\n`;
        appendToLog(sessionHeader);
        break;

      case 'conversation':
        const conversationEntry = `User question: ${userQuestion}\nAI Answer: ${aiAnswer}\n\n`;
        appendToLog(conversationEntry);
        break;

      case 'error':
        const errorEntry = `ERROR: ${error}${context ? ` (Context: ${context})` : ''}\nTimestamp: ${formatTimestamp(timestamp)}\n\n`;
        appendToLog(errorEntry);
        break;

      default:
        return res.status(400).json({ message: 'Invalid log type' });
    }

    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Logging error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}

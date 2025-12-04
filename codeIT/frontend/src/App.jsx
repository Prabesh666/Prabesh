import { useCallback, useEffect, useMemo, useState } from "react";
import Header from "./components/Header.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import { sendMessage, fetchHealth } from "./services/api.js";

const SESSION_KEY = "codeit-chatbot-session";
const HISTORY_KEY = "codeit-chatbot-history";

const readLocalValue = (key, fallback) => {
  if (typeof window === "undefined") {
    return fallback;
  }
  try {
    const value = window.localStorage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch (error) {
    console.warn(`Failed to parse local storage key ${key}`, error);
    return fallback;
  }
};

const writeLocalValue = (key, value) => {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(key, JSON.stringify(value));
};

const App = () => {
  const [sessionId, setSessionId] = useState(() => readLocalValue(SESSION_KEY, null));
  const [history, setHistory] = useState(() => readLocalValue(HISTORY_KEY, []));
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const [serviceOnline, setServiceOnline] = useState(true);

  useEffect(() => {
    fetchHealth()
      .then(() => setServiceOnline(true))
      .catch(() => setServiceOnline(false));
  }, []);

  useEffect(() => {
    writeLocalValue(SESSION_KEY, sessionId);
  }, [sessionId]);

  useEffect(() => {
    writeLocalValue(HISTORY_KEY, history);
  }, [history]);

  const handleReset = useCallback(() => {
    setHistory([]);
    setSessionId(null);
    setError(null);
    writeLocalValue(HISTORY_KEY, []);
    writeLocalValue(SESSION_KEY, null);
  }, []);

  const handleSend = useCallback(
    async (message) => {
      setError(null);
      const previousHistory = history;
      const optimisticTimestamp = new Date().toISOString();
      const optimisticHistory = [
        ...previousHistory,
        { role: "user", content: message, timestamp: optimisticTimestamp },
      ];
      setHistory(optimisticHistory);
      setIsTyping(true);

      try {
        const response = await sendMessage({ message, sessionId });
        const nextSessionId = response.session_id;
        const nextHistory = response.history.map((turn) => ({
          role: turn.role,
          content: turn.content,
          timestamp: turn.timestamp,
        }));
        setHistory(nextHistory);
        setSessionId(nextSessionId);
        setServiceOnline(true);
      } catch (requestError) {
        setError(requestError.message);
        setHistory(previousHistory);
        setServiceOnline(false);
      } finally {
        setIsTyping(false);
      }
    },
    [history, sessionId]
  );

  const statusMessage = useMemo(() => {
    if (serviceOnline) {
      return "Online";
    }
    return "Offline";
  }, [serviceOnline]);

  return (
    <div className="app-shell">
      <Header />
      <div className="status-chip" data-status={serviceOnline ? "online" : "offline"}>
        Service {statusMessage}
      </div>
      <ChatWindow history={history} onSend={handleSend} onReset={handleReset} isTyping={isTyping} error={error} />
    </div>
  );
};

export default App;

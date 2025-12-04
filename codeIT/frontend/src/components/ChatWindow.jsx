import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import clsx from "clsx";
import MessageBubble from "./MessageBubble.jsx";

const ChatWindow = ({ history, onSend, onReset, isTyping, error }) => {
  const [input, setInput] = useState("");
  const messageListRef = useRef(null);

  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTo({ top: messageListRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [history, isTyping]);

  const handleSubmit = (event) => {
    event.preventDefault();
    const value = input.trim();
    if (!value) {
      return;
    }
    onSend(value);
    setInput("");
  };

  return (
    <section className="chat-window">
      <div className="chat-window__body" ref={messageListRef}>
        {history.length > 0 && (
          <div className="chat-window__toolbar">
            <button type="button" className="ghost-button" onClick={onReset}>
              Start New Conversation
            </button>
          </div>
        )}

        {history.length === 0 && (
          <motion.div
            className="chat-empty"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h2>Namaste! 👋</h2>
            <p>Ask me about courses, schedules, mentors, scholarships, or campus life.</p>
          </motion.div>
        )}

        {history.map((turn, index) => (
          <MessageBubble key={`${turn.role}-${index}-${turn.timestamp}`} role={turn.role} content={turn.content} timestamp={turn.timestamp} />
        ))}

        {isTyping && (
          <motion.div
            className="typing-indicator"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </motion.div>
        )}
      </div>

      {error && (
        <div className="chat-error">
          <strong>Oops!</strong> {error}
        </div>
      )}

      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea
          className="chat-input"
          placeholder="Type your question..."
          value={input}
          onChange={(event) => setInput(event.target.value)}
          rows={1}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              handleSubmit(event);
            }
          }}
        />
        <button type="submit" className={clsx("chat-submit", { "chat-submit--disabled": !input.trim() })} disabled={!input.trim()}>
          Send
        </button>
      </form>
    </section>
  );
};

export default ChatWindow;

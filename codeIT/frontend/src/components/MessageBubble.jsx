import { motion } from "framer-motion";
import clsx from "clsx";

const MessageBubble = ({ role, content, timestamp }) => {
  const isUser = role === "user";
  const timeLabel = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : null;

  return (
    <motion.article
      className={clsx("message-bubble", isUser ? "message-bubble--user" : "message-bubble--assistant")}
      initial={{ opacity: 0, y: 8, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
    >
      <div className="message-bubble__inner">
        {!isUser && <div className="avatar">🤖</div>}
        <p>{content}</p>
      </div>
      {timeLabel && <span className="message-timestamp">{timeLabel}</span>}
    </motion.article>
  );
};

export default MessageBubble;

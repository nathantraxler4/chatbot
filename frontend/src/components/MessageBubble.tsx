import "./MessageBubble.css";

const MessageBubble = ({
  author,
  message,
}: {
  author: string;
  message: string;
}) => {
  return (
    <div className={`message ${author}`}>
      <p className="messagetext">{message}</p>
    </div>
  );
};

export default MessageBubble;

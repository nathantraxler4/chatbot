import ActionButton from "./ActionButton";
import "./MessageBubble.css";
import { FaRegEdit } from "react-icons/fa";
import { MdDelete } from "react-icons/md";

const MessageBubble = ({
  author,
  message,
}: {
  author: string;
  message: string;
}) => {
  return (
    <div className={`message-container ${author}`}>
      {author === "user" && (
        <div className="message-actions-container">
          <ActionButton Icon={MdDelete} />
          <ActionButton Icon={FaRegEdit} />
        </div>
      )}
      <div className={`message ${author}`}>
        <p>{message}</p>
      </div>
    </div>
  );
};

export default MessageBubble;

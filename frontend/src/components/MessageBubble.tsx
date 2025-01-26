import ActionButton from "./ActionButton";
import { Message } from "./ChatWindow";
import "./MessageBubble.css";
import { FaRegEdit } from "react-icons/fa";
import { MdDelete } from "react-icons/md";

type MessageBubbleParams = {
  message: Message;
  onDelete: (id: number) => void;
};

const MessageBubble = ({ message, onDelete }: MessageBubbleParams) => {
  return (
    <div className={`message-container ${message.author}`}>
      {message.author === "user" && (
        <div className="message-actions-container">
          <ActionButton
            Icon={MdDelete}
            onClickHandler={() => onDelete(message.id)}
          />
          <ActionButton Icon={FaRegEdit} onClickHandler={() => {}} />
        </div>
      )}
      <div className={`message ${message.author}`}>
        <p>{message.message}</p>
      </div>
    </div>
  );
};

export default MessageBubble;

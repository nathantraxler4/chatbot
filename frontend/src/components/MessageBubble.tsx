import { KeyboardEventHandler, useState } from "react";
import ActionButton from "./ActionButton";
import { Message } from "./ChatWindow";
import "./MessageBubble.css";
import { FaRegEdit } from "react-icons/fa";
import { MdDelete } from "react-icons/md";
import { MdCheck } from "react-icons/md";

type MessageBubbleParams = {
  message: Message;
  onDelete: (id: number) => void;
  onEditSave: (id: number, editText: string) => void;
};

const MessageBubble = ({
  message,
  onDelete,
  onEditSave,
}: MessageBubbleParams) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(message.message);

  const handleEnterDown: KeyboardEventHandler<HTMLInputElement> = (e) => {
    console.log(e.key);
    if (e.key === "Enter") {
      onEditSave(message.id, editText);
      setIsEditing(false);
    } else if (e.key === "Escape") {
      setIsEditing(false);
      setEditText(message.message);
    }
  };

  return (
    <div className={`message-container ${message.author}`}>
      {message.author === "user" && (
        <div className="message-actions-container">
          <ActionButton
            Icon={MdDelete}
            onClickHandler={() => onDelete(message.id)}
          />
          <ActionButton
            Icon={FaRegEdit}
            onClickHandler={() =>
              setIsEditing((prevIsEditing) => !prevIsEditing)
            }
          />
        </div>
      )}
      {isEditing ? (
        <div className="edit-container">
          <input
            type="text"
            value={editText}
            placeholder='Press "Enter" to save and "Escape" to exit.'
            className="edit-input"
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setEditText(e.target.value)
            }
            onKeyDown={handleEnterDown}
          />
          <button
            onClick={() => {
              onEditSave(message.id, editText);
              setIsEditing(false);
            }}
            className="edit-save-button"
          >
            <MdCheck className="edit-save-icon" />
          </button>
        </div>
      ) : (
        <div className={`message ${message.author}`}>
          <p>{message.message}</p>
        </div>
      )}
    </div>
  );
};

export default MessageBubble;

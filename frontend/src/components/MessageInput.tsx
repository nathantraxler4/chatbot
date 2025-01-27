import React, { KeyboardEventHandler, useState } from "react";
import "./MessageInput.css";
import { FaArrowRight } from "react-icons/fa";

type MessageInputProps = {
  onSendMessage: (message: string) => void;
};

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage }) => {
  const [userInput, setUserInput] = useState<string>("");

  const handleSendMessage = () => {
    if (userInput.trim()) {
      onSendMessage(userInput);
      setUserInput("");
    }
  };

  const handleEnterDown: KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  return (
    <div className="message-input-container">
      <input
        type="text"
        value={userInput}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
          setUserInput(e.target.value)
        }
        onKeyDown={handleEnterDown}
        placeholder="Your question"
        className="message-input"
      />
      <button onClick={handleSendMessage} className="send-button">
        <FaArrowRight className="send-arrow" />
      </button>
    </div>
  );
};

export default MessageInput;

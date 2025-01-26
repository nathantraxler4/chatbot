import React, { useState } from "react";
import "./MessageInput.css";
import { FaArrowRight } from "react-icons/fa";

type MessageInputProps = {
  onSendMessage: (message: string) => void;
};

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage }) => {
  const [userInput, setUserInput] = useState<string>("");

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(event.target.value);
  };

  const handleSendMessage = () => {
    if (userInput.trim()) {
      onSendMessage(userInput);
      setUserInput("");
    }
  };

  return (
    <div className="message-input-container">
      <input
        type="text"
        value={userInput}
        onChange={handleChange}
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

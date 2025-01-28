import MessageBubble from "./MessageBubble";
import MessageInput from "./MessageInput";
import "./ChatWindow.css";
import { useEffect, useRef, useState } from "react";
import { Session } from "@supabase/supabase-js";

export type Message = {
  id: number;
  author: string;
  message: string;
};

const ChatWindow = ({ session }: { session: Session }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>();
  const prevMessageCountRef = useRef<number | undefined>(undefined);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async (userInput: string) => {
    try {
      setErrorMessage(null);
      const response = await fetch("http://localhost:8000/message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({ message: userInput }),
      });

      if (!response.ok) {
        throw new Error(response.statusText);
      }

      const responseBody = await response.json();

      setMessages((prevMessages) => {
        return [...prevMessages, ...responseBody.exchange];
      });
    } catch (error) {
      setErrorMessage("Something went wrong. Please try again!");
      console.error("Error sending message:", error);
    }
  };

  const handleDeleteMessage = async (messageId: number) => {
    try {
      setErrorMessage(null);
      const response = await fetch(
        `http://localhost:8000/message/${messageId}`,
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session.access_token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(response.statusText);
      }

      setMessages((prevMessages) =>
        prevMessages.filter((msg) => msg.id !== messageId)
      );
    } catch (error) {
      setErrorMessage("Something went wrong. Please try again!");
      console.error("Error sending message:", error);
    }
  };

  const handleEditMessage = async (messageId: number, editText: string) => {
    try {
      setErrorMessage(null);
      const response = await fetch(
        `http://localhost:8000/message/${messageId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({ message: editText }),
        }
      );

      if (!response.ok) {
        throw new Error(response.statusText);
      }

      const data = await response.json();

      setMessages((prevMessages) => {
        return prevMessages.map((msg) =>
          msg.id === data.id ? { ...msg, message: data.message } : msg
        );
      });
    } catch (error) {
      setErrorMessage("Something went wrong. Please try again!");
      console.error("Error sending message:", error);
    }
  };

  // Ensure we only scroll to the bottom when a message is sent
  useEffect(() => {
    if (messages.length - (prevMessageCountRef.current ?? 0) > 0)
      scrollToBottom();
    prevMessageCountRef.current = messages.length;
  }, [messages]);

  return (
    <div className="chatwindow">
      <div className="messages-container">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onDelete={handleDeleteMessage}
            onEditSave={handleEditMessage}
          />
        ))}
        {/* So we can programmatically scroll here when message is sent. */}
        <div ref={messagesEndRef} />
      </div>
      {errorMessage && <div className="error-message">{errorMessage}</div>}
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
};

export default ChatWindow;

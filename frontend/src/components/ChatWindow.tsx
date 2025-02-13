import MessageBubble from "./MessageBubble";
import MessageInput from "./MessageInput";
import "./ChatWindow.css";
import { useEffect, useRef, useState } from "react";
import { Session } from "@supabase/supabase-js";
import * as api from "../api";

export type Message = {
  id: number;
  author: string;
  message: string;
};

const ChatWindow = ({ session }: { session: Session }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>();
  const prevMessageCountRef = useRef<number | undefined>(undefined);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async (userInput: string) => {
    try {
      setErrorMessage(null);
      setLoading(true);

      const sentMessage = {
        id: -1,
        message: userInput,
        author: "user",
      };

      // Placeholder while waiting for response message with id
      setMessages((prevMessages) => {
        return [...prevMessages, sentMessage];
      });

      const responseBody = await api.postMessage(
        userInput,
        session.access_token
      );

      setMessages((prevMessages) => {
        return [
          ...prevMessages.filter((msg) => msg.id !== -1),
          ...responseBody.exchange,
        ];
      });
    } catch (error) {
      // Remove message that did not get response
      setMessages((prevMessages) => {
        return [...prevMessages.filter((msg) => msg.id !== -1)];
      });
      setErrorMessage("Something went wrong. Please try again!");
      console.error("Error sending message:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteMessage = async (messageId: number) => {
    try {
      setErrorMessage(null);
      await api.deleteMessage(messageId, session.access_token);
      setMessages((prevMessages) =>
        prevMessages.filter((msg) => msg.id !== messageId)
      );
    } catch (error) {
      setErrorMessage("Something went wrong. Please try again!");
      console.error("Error sending message:", error);
    }
  };

  const handleEditMessage = async (messageId: number, editText: string) => {
    const prevMessage = messages.find((m) => m.id === messageId) as Message;
    try {
      setErrorMessage(null);
      setMessages((prevMessages) => {
        return prevMessages.map((msg) =>
          msg.id === messageId ? { ...msg, message: editText } : msg
        );
      });
      await api.editMessage(messageId, editText, session.access_token);
    } catch (error) {
      setMessages((prevMessages) => {
        return prevMessages.map((msg) =>
          msg.id === messageId ? { ...prevMessage } : msg
        );
      });
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
      {messages.length === 0 && (
        <div className={`welcome-text`}>
          <p>Hi! Ask me anything...</p>
        </div>
      )}
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
      <MessageInput loading={loading} onSendMessage={handleSendMessage} />
    </div>
  );
};

export default ChatWindow;

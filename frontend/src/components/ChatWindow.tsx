import MessageBubble from "./MessageBubble";
import "./ChatWindow.css";

const mockMessages = [
  {
    id: 1,
    author: "user",
    message: "User Message 1",
  },
  {
    id: 2,
    author: "chatbot",
    message: "Chatbot Message 1",
  },
  {
    id: 3,
    author: "user",
    message: "User Message 2",
  },
  {
    id: 4,
    author: "chatbot",
    message: "Chatbot Message 2",
  },
  {
    id: 5,
    author: "user",
    message: "User Message 1",
  },
  {
    id: 6,
    author: "chatbot",
    message: "Chatbot Message 1",
  },
  {
    id: 7,
    author: "user",
    message:
      "User Message 2 User Message 2 User Message 2User Message 2 User Message 2 User Message 2 User Message 2 User Message 2",
  },
  {
    id: 8,
    author: "chatbot",
    message:
      "Chatbot Message 2 Chatbot Message 2 Chatbot Message 2 Chatbot Message 2 Chatbot Message 2 Chatbot Message 2",
  },
  {
    id: 9,
    author: "user",
    message: "User Message 1",
  },
  {
    id: 10,
    author: "chatbot",
    message: "Chatbot Message 1",
  },
  {
    id: 11,
    author: "user",
    message: "User Message 2",
  },
  {
    id: 12,
    author: "chatbot",
    message: "Chatbot Message 2",
  },
  {
    id: 13,
    author: "user",
    message: "User Message 1",
  },
  {
    id: 14,
    author: "chatbot",
    message: "Chatbot Message 1",
  },
  {
    id: 15,
    author: "user",
    message: "User Message 2",
  },
  {
    id: 16,
    author: "chatbot",
    message: "Chatbot Message 2",
  },
];

const ChatWindow = () => {
  return (
    <div className="chatwindow">
      {mockMessages.map((msg) => (
        <MessageBubble key={msg.id} author={msg.author} message={msg.message} />
      ))}
    </div>
  );
};

export default ChatWindow;

import { useState } from "react";
import "./App.css";
import ChatWindow from "./components/ChatWindow";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <ChatWindow />
    </>
  );
}

export default App;

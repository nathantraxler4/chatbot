const host = "https://nathans-chatbot-server-7d392ec059e8.herokuapp.com";

export async function postMessage(messageText: string, session_token: string) {
  const response = await fetch(`${host}/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session_token}`,
    },
    body: JSON.stringify({ message: messageText }),
  });

  if (!response.ok) {
    throw new Error(response.statusText);
  }

  const responseBody = await response.json();

  return responseBody;
}

export async function editMessage(
  messageId: number,
  editText: string,
  session_token: string
) {
  const response = await fetch(`${host}/message/${messageId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session_token}`,
    },
    body: JSON.stringify({ message: editText }),
  });

  if (!response.ok) {
    throw new Error(response.statusText);
  }

  const data = await response.json();
  return data;
}

export async function deleteMessage(messageId: number, session_token: string) {
  const response = await fetch(`${host}/message/${messageId}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session_token}`,
    },
  });

  if (!response.ok) {
    throw new Error(response.statusText);
  }
}

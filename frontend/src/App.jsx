import { useState, useRef, useEffect } from 'react';
import { FaPaperPlane, FaEllipsisV, FaCheck } from 'react-icons/fa';
import './App.css';

export default function App() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const characters = {
    ammavan: { name: "Ammavan 👨", color: "bg-blue-100" },
    ammayi: { name: "Ammayi 👩", color: "bg-purple-100" },
    ammu: { name: "Ammu 👧", color: "bg-pink-100" },
    appooppan: { name: "Appooppan 👴", color: "bg-green-100" }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const userMessage = input.trim();
    if (!userMessage || loading) return;

    // Add user message
    setMessages(prev => [...prev, {
      id: Date.now(),
      text: userMessage,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isUser: true
    }]);
    
    setLoading(true);
    setInput('');

    try {
      for (const [charKey, charData] of Object.entries(characters)) {
        try {
          const response = await fetch('http://localhost:5000/api/respond', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ character: charKey, text: userMessage })
          });

          const data = await response.json();
          
          if (data.status === "success") {
            setMessages(prev => [...prev, {
              id: Date.now() + Math.random(),
              sender: charData.name,
              text: data.response,
              time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              color: charData.color,
              isUser: false
            }]);
          }

          await new Promise(resolve => setTimeout(resolve, 800));
          
        } catch (err) {
          console.error(`Error from ${charData.name}:`, err);
          setMessages(prev => [...prev, {
            id: Date.now() + Math.random(),
            sender: charData.name,
            text: "Temporary error - try again",
            color: charData.color,
            isUser: false
          }]);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const testApiConnection = async () => {
    try {
      const response = await fetch('http://localhost:5000/test');
      const data = await response.json();
      alert(`Backend status: ${data.status}`);
    } catch (err) {
      alert('Failed to connect to backend');
    }
  };

  return (
    <div className="phone-mockup">
      <div className="whatsapp-header">
        <div className="header-content">
          <h1>Mallu Relatives</h1>
          <p>Online</p>
        </div>
        <button onClick={testApiConnection} className="test-button">
          Test API
        </button>
        <FaEllipsisV className="header-icon" />
      </div>

      <div className="chat-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.isUser ? 'user' : 'character'}`}>
            {!msg.isUser && <div className="sender-avatar">{msg.sender.charAt(0)}</div>}
            <div className="message-content">
              {!msg.isUser && <div className="sender-name">{msg.sender}</div>}
              <div className={`bubble ${msg.isUser ? 'user-bubble' : msg.color}`}>
                {msg.text}
                <div className="message-time">{msg.time}</div>
              </div>
            </div>
          </div>
        ))}
        {loading && <div className="typing-indicator">Typing...</div>}
      </div>

      <form onSubmit={handleSubmit} className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          <FaPaperPlane />
        </button>
      </form>
    </div>
  );
}
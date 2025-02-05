import React, { useState } from 'react';
import { Bot, Send, ArrowRight, ShoppingCart, TrendingUp, MessageSquare, Sparkles, Zap } from 'lucide-react';

interface Message {
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  status?: string;
}

function App() {
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage(''); // Clear input immediately after sending
    setLoading(true);
    
    try {
      const res = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content }),
      });
      
      const data = await res.json();
      const assistantMessage: Message = {
        type: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
        status: data.status
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        type: 'assistant',
        content: 'Sorry, there was an error processing your request.',
        timestamp: new Date().toISOString(),
        status: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const examples = [
    {
      icon: <ShoppingCart className="w-6 h-6 text-emerald-500" />,
      title: "Smart Bargaining",
      description: "Negotiate and purchase items from vendors with automated price comparison"
    },
    {
      icon: <TrendingUp className="w-6 h-6 text-blue-500" />,
      title: "Financial Assets",
      description: "Buy crypto or stocks through intelligent market analysis"
    }
  ];

  const samplePrompts = [
    "Buy 200 chocolates from Kiran if price is under $1 each",
    "Purchase 50 AAPL stocks if price drops below $170",
    "Get quotes for 1000 t-shirts from local vendors",
    "Buy 2 ETH if price is below $3000"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 text-black flex">
      {/* Sidebar */}
      <div className="w-1/4 border-r border-gray-200 p-6 bg-white shadow-sm">
        <div className="flex items-center space-x-3 mb-8">
          <div className="p-2 bg-black rounded-xl">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold">Sudheer's IntelliPay</h1>
        </div>

        <div className="space-y-6">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <h2 className="text-lg font-semibold">Try these prompts</h2>
            </div>
            <div className="space-y-3">
              {samplePrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setInputMessage(prompt)}
                  className="w-full text-left p-3.5 text-sm border border-gray-200 rounded-xl hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 group"
                >
                  <div className="flex items-center">
                    <Zap className="w-4 h-4 text-gray-400 group-hover:text-purple-500 transition-colors mr-2" />
                    {prompt}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Chat History */}
        <div className="flex-1 p-6 overflow-auto">
          {messages.length === 0 ? (
            /* Capabilities Section */
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                What I can help you with
                <div className="h-1 w-1 bg-gray-300 rounded-full mx-3" />
                <span className="text-sm font-normal text-gray-500">Select a capability to get started</span>
              </h2>
              <div className="grid grid-cols-2 gap-4">
                {examples.map((example, index) => (
                  <div 
                    key={index} 
                    className="p-5 border border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-sm transition-all duration-200 bg-white"
                  >
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="p-2 bg-gray-50 rounded-lg">
                        {example.icon}
                      </div>
                      <h3 className="font-medium">{example.title}</h3>
                    </div>
                    <p className="text-sm text-gray-600">{example.description}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            /* Chat Messages */
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] p-4 rounded-xl ${
                      message.type === 'user'
                        ? 'bg-black text-white'
                        : 'bg-white border border-gray-200'
                    }`}
                  >
                    <p className={message.type === 'user' ? 'text-white' : 'text-gray-700'}>
                      {message.content}
                    </p>
                    <div className="mt-2 text-xs flex items-center space-x-2">
                      <span className={`${message.type === 'user' ? 'text-gray-300' : 'text-gray-500'}`}>
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </span>
                      {message.status && (
                        <>
                          <span className="inline-block w-1 h-1 rounded-full bg-gray-400" />
                          <span className="text-gray-500">Status: {message.status}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Input Form */}
        <div className="border-t border-gray-200 p-6 bg-white">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Enter your request (e.g., 'Buy 200 chocolates from Kiran...')"
              className="flex-1 p-3.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent transition-all"
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="px-6 py-3.5 bg-black text-white rounded-xl hover:bg-gray-800 transition-colors disabled:opacity-50 flex items-center space-x-2 shadow-sm"
            >
              {loading ? (
                'Processing...'
              ) : (
                <>
                  <span>Send</span>
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
          <p className="mt-3 text-sm text-gray-500 flex items-center">
            <span className="inline-block w-1 h-1 rounded-full bg-gray-400 mr-2" />
            Currently using PayMan APIs for test transactions. Can be integrated with Stripe SDK for production use.
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
'use client';

import { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/context/auth-context';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date | string;
  tool_calls?: any[];
}

export default function FloatingChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  // Close chat when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isOpen && !(event.target as Element).closest('.chat-widget')) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Load conversation history from localStorage on component mount
  useEffect(() => {
    if (user && user.id) {
      const savedConversations = localStorage.getItem(`chat_history_${user.id}`);
      if (savedConversations) {
        try {
          const parsedConversations = JSON.parse(savedConversations);
          // Convert string timestamps back to Date objects
          const messagesWithDateObjects = parsedConversations.map((msg: Message) => ({
            ...msg,
            timestamp: typeof msg.timestamp === 'string' ? new Date(msg.timestamp) : msg.timestamp
          }));
          setMessages(messagesWithDateObjects);
        } catch (e) {
          console.error('Error parsing saved chat history:', e);
        }
      }
    }
  }, [user]);

  // Save conversation history to localStorage whenever messages change
  useEffect(() => {
    if (user && user.id && messages.length > 0) {
      // Convert Date objects to ISO strings for proper serialization
      const serializableMessages = messages.map(msg => ({
        ...msg,
        timestamp: typeof msg.timestamp === 'string' ? msg.timestamp : msg.timestamp.toISOString()
      }));
      localStorage.setItem(`chat_history_${user.id}`, JSON.stringify(serializableMessages));
    }
  }, [messages, user]);

  // Scroll to bottom of messages when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Clear chat history function
  const clearChatHistory = () => {
    if (user && user.id) {
      localStorage.removeItem(`chat_history_${user.id}`);
      setMessages([]);
      setConversationId(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading || !user) return;

    // Add user message to the chat
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // Call the AI agent endpoint
      if (!user || !user.id) {
        throw new Error('User not authenticated');
      }

      const response = await api.chatWithAgent(inputValue, user.id.toString(), conversationId || undefined);

      if (!response.success) {
        throw new Error(response.message || 'Failed to get response from AI agent');
      }

      // Set conversation ID if not already set
      if (!conversationId && response.data?.conversation_id) {
        setConversationId(response.data.conversation_id);
      }

      // Add AI response to the chat
      const aiMessage: Message = {
        id: Date.now().toString(),
        content: response.data.response,
        role: 'assistant',
        timestamp: new Date(),
        tool_calls: response.data.tool_calls,
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err instanceof Error ? err.message : 'An error occurred while sending the message');

      // Add error message to the chat
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Floating Chat Button */}
      <button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 z-[9999] bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-full shadow-2xl hover:from-blue-600 hover:to-purple-700 transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-opacity-50 border-2 border-white transform hover:scale-110"
        aria-label="Open AI assistant"
        style={{ width: '60px', height: '60px', bottom: '24px', right: '24px' }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v17l3-3 3 3V3M7 21h10M5 7h14M5 11h14M7 3h10a2 2 0 012 2v1a1 1 0 01-1 1H6a1 1 0 01-1-1V5a2 2 0 012-2z" />
        </svg>
      </button>

      {/* Chat Panel - Slide in from right */}
      {isOpen && (
        <div className="chat-widget fixed bottom-24 right-6 z-40 w-80 h-96 bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col transform transition-transform duration-300 ease-in-out">
          {/* Chat Header */}
          <div className="bg-blue-600 text-white p-3 rounded-t-lg flex justify-between items-center">
            <h3 className="font-semibold">AI Robot Assistant</h3>
            <div className="flex space-x-2">
              {messages.length > 0 && (
                <button
                  onClick={clearChatHistory}
                  className="text-white hover:text-gray-200 focus:outline-none"
                  aria-label="Clear chat history"
                  title="Clear chat history"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              )}
              <button
                onClick={toggleChat}
                className="text-white hover:text-gray-200 focus:outline-none"
                aria-label="Close chat"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-gray-50">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center p-4">
                <div className="bg-blue-100 p-3 rounded-full mb-3">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h4 className="text-lg font-medium text-gray-800 mb-1">Need help?</h4>
                <p className="text-sm text-gray-600">
                  I can help you manage your tasks. Try asking me to add, list, complete, or delete tasks.
                </p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-3 py-2 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 text-gray-800'
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                    {message.tool_calls && message.tool_calls.length > 0 && (
                      <div className="mt-1 text-xs opacity-75">
                        <p>Tools executed:</p>
                        <ul className="list-disc pl-3 mt-1">
                          {message.tool_calls.map((call, idx) => (
                            <li key={idx}>{call.name}: {JSON.stringify(call.arguments)}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                      {(typeof message.timestamp === 'string' ? new Date(message.timestamp) : message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 text-gray-800 px-3 py-2 rounded-lg max-w-xs">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-2 bg-white">
            {error && (
              <div className="mb-2 p-2 bg-red-100 text-red-700 rounded text-xs">
                Error: {error}
              </div>
            )}
            <form onSubmit={handleSubmit} className="flex space-x-1">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 border border-gray-300 rounded-lg px-3 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                disabled={isLoading}
                autoComplete="off"
              />
              <button
                type="submit"
                className={`px-3 py-1 rounded-lg text-white text-sm ${
                  isLoading ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'
                }`}
                disabled={isLoading || !inputValue.trim()}
              >
                Send
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
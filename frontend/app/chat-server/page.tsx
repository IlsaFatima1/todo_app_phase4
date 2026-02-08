import { initializeConversation } from '@/actions/chatActions';
import ChatFormServer from '@/components/ChatFormServer';
import { cookies } from 'next/headers';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  tool_calls?: any[];
}

export default async function ChatServerPage() {
  // Get user info from cookies or session
  const cookieStore = cookies();
  const userId = cookieStore.get('user_id')?.value || '1'; // Default to user ID 1 for demo

  // Initialize conversation
  const { success, conversationId } = await initializeConversation(userId);
  const initialConversationId = success ? conversationId : null;

  // Initial empty messages
  const initialMessages: Message[] = [];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="bg-white border-b border-gray-200 p-4">
        <h1 className="text-xl font-semibold text-gray-800">Todo AI Assistant (Server)</h1>
        <p className="text-sm text-gray-500">Manage your tasks with natural language</p>
      </div>

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 flex-grow">
        {initialMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <h2 className="text-xl font-medium text-gray-700 mb-2">Welcome to Todo AI Assistant!</h2>
            <p className="text-gray-500 max-w-md">
              I can help you manage your tasks. Try asking me to add, list, complete, or delete tasks.
              For example: "Add a task to buy groceries" or "Show me my pending tasks".
            </p>
          </div>
        ) : (
          initialMessages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                {message.tool_calls && message.tool_calls.length > 0 && (
                  <div className="mt-2 text-xs opacity-75">
                    <p>Tools executed:</p>
                    <ul className="list-disc pl-4">
                      {message.tool_calls.map((call, idx) => (
                        <li key={idx}>{call.name}: {JSON.stringify(call.arguments)}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <ChatFormServer
          userId={userId}
          conversationId={initialConversationId || undefined}
        />
        <p className="text-xs text-gray-500 mt-2">
          Example: "Add a task to buy groceries" or "Show me my pending tasks"
        </p>
      </div>
    </div>
  );
}
'use client';

import { useFormState, useFormStatus } from 'react-dom';
import { sendMessageToAgent } from '@/actions/chatActions';
import { useState } from 'react';

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className={`px-4 py-2 rounded-md text-white ${
        pending ? 'bg-blue-400' : 'bg-blue-500 hover:bg-blue-600'
      }`}
    >
      {pending ? 'Sending...' : 'Send'}
    </button>
  );
}

export default function ChatFormServer({ userId, conversationId }: { userId: string; conversationId?: string }) {
  const [message, setMessage] = useState('');
  const [state, formAction] = useFormState(sendMessageToAgent, {
    success: false,
    error: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim()) return;

    const formData = new FormData();
    formData.set('message', message);
    formData.set('user_id', userId);
    if (conversationId) {
      formData.set('conversation_id', conversationId);
    }

    formAction(formData);
    setMessage('');
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message here..."
          className="flex-1 p-3 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        <SubmitButton />
      </div>
      {state.error && (
        <p className="mt-2 text-sm text-red-600">{state.error}</p>
      )}
    </form>
  );
}
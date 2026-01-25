'use client';

import { useFormState, useFormStatus } from 'react-dom';
import { createTodo } from '@/actions/todoActions';
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
      {pending ? 'Adding...' : 'Add Todo'}
    </button>
  );
}

export default function TodoFormServer() {
  const [title, setTitle] = useState('');
  const [state, formAction] = useFormState(createTodo, {
    success: false,
    error: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const formData = new FormData();
    formData.set('title', title);

    formAction(formData);
    setTitle('');
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <div className="flex gap-2">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Add a new task..."
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
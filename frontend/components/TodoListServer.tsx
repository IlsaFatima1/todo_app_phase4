'use client';

import { Todo } from '@/types/todo';
import { useState } from 'react';
import { toggleTodoCompletion, deleteTodo } from '@/actions/todoActions';

interface TodoListProps {
  todos: Todo[];
}

export default function TodoListServer({ todos }: TodoListProps) {
  const [todoList, setTodoList] = useState<Todo[]>(todos);

  const handleToggle = async (id: string, completed: boolean) => {
    const result = await toggleTodoCompletion(id, completed);

    if (result.success) {
      setTodoList(prev =>
        prev.map(todo =>
          todo.id === id ? { ...todo, completed: !completed } : todo
        )
      );
    }
  };

  const handleDelete = async (id: string) => {
    const result = await deleteTodo(id);

    if (result.success) {
      setTodoList(prev => prev.filter(todo => todo.id !== id));
    }
  };

  return (
    <div className="space-y-2">
      {todoList.length === 0 ? (
        <p className="text-gray-500 text-center py-4">No todos yet</p>
      ) : (
        todoList.map((todo) => (
          <div
            key={todo.id}
            className={`flex items-center justify-between p-4 bg-white rounded-lg shadow ${
              todo.completed ? 'opacity-75' : ''
            }`}
          >
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={todo.completed}
                onChange={() => handleToggle(todo.id, todo.completed)}
                className="mr-3 h-5 w-5"
              />
              <span
                className={`${todo.completed ? 'line-through text-gray-500' : 'text-gray-800'}`}
              >
                {todo.title}
              </span>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handleDelete(todo.id)}
                className="text-red-500 hover:text-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
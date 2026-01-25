'use client';

import { useState, useEffect } from 'react';
import TodoForm from '@/components/TodoForm';
import TodoList from '@/components/TodoList';
import { Todo } from '@/types/todo';
import { api } from '@/lib/api';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import FloatingChatWidget from '@/components/FloatingChatWidget';
import { useAuth } from '@/context/auth-context';

// ProfileImage component for consistent avatar display
const ProfileImage = ({ imageUrl, initials }: { imageUrl: string; initials: string }) => {
  const [hasError, setHasError] = useState(false);

  if (hasError) {
    return (
      <div className="w-full h-full bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
        {initials}
      </div>
    );
  }

  return (
    <img
      src={imageUrl}
      alt="Profile"
      className="w-full h-full object-cover rounded-full"
      onError={() => setHasError(true)}
    />
  );
};

export default function TodosPage() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  // Load todos on component mount
  useEffect(() => {
    const fetchTodos = async () => {
      try {
        setLoading(true);
        const response = await api.getTodos();
        setTodos(response.data as Todo[]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchTodos();
  }, []);

  const handleAddTodo = async (title: string) => {
    try {
      const response = await api.createTodo({ title });
      setTodos(prev => [...prev, response.data as Todo]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleToggleTodo = async (id: string) => {
    const todo = todos.find(t => t.id === id);
    if (todo) {
      try {
        const response = await api.updateTodo(id, { completed: !todo.completed });
        setTodos(prev =>
          prev.map(t =>
            t.id === id ? response.data as Todo : t
          )
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      }
    }
  };

  const handleUpdateTodo = async (id: string, title: string) => {
    try {
      const response = await api.updateTodo(id, { title });
      setTodos(prev =>
        prev.map(t =>
          t.id === id ? response.data as Todo : t
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleDeleteTodo = async (id: string) => {
    try {
      await api.deleteTodo(id);
      setTodos(prev => prev.filter(t => t.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  // Filter todos based on selection
  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.completed;
    if (filter === 'completed') return todo.completed;
    return true;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <ProtectedRoute>
          <div className="flex">
            {/* Left Sidebar */}
            <div className="w-64 bg-gray-100 min-h-screen p-4">
              <h1 className="text-xl font-bold mb-6">Todo App</h1>
              <nav>
                <ul className="space-y-2">
                  <li>
                    <a href="/todos" className="flex items-center p-2 bg-gray-200 rounded">Todos</a>
                  </li>
                  <li>
                    <a href="/profile" className="flex items-center p-2 hover:bg-gray-200 rounded">Profile</a>
                  </li>
                  <li>
                    <a href="/settings" className="flex items-center p-2 hover:bg-gray-200 rounded">Settings</a>
                  </li>
                </ul>
              </nav>
            </div>

            {/* Main Content */}
            <div className="flex-1 p-8">
              <div className="flex justify-between items-center mb-8">
                <h2 className="text-lg">Todo App / Todos</h2>
                <div className="w-8 h-8 rounded-full overflow-hidden">
                  {useAuth().user?.profile_picture ? (
                    <ProfileImage
                      imageUrl={api.getProfilePictureUrl(useAuth().user.profile_picture)}
                      initials={useAuth().user?.name?.charAt(0)?.toUpperCase() || 'U'}
                    />
                  ) : (
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {useAuth().user?.name?.charAt(0)?.toUpperCase() || 'U'}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-center items-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
              </div>
            </div>
          </div>
        </ProtectedRoute>

        {/* Floating Chat Widget - Always visible regardless of auth status */}
        <FloatingChatWidget />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <ProtectedRoute>
        <div className="flex">
          {/* Left Sidebar */}
          <div className="w-64 bg-gray-100 min-h-screen p-4">
            <h1 className="text-xl font-bold mb-6">Todo App</h1>
            <nav>
              <ul className="space-y-2">
                <li>
                  <a href="/todos" className="flex items-center p-2 bg-gray-200 rounded">Todos</a>
                </li>
                <li>
                  <a href="/profile" className="flex items-center p-2 hover:bg-gray-200 rounded">Profile</a>
                </li>
                <li>
                  <a href="/settings" className="flex items-center p-2 hover:bg-gray-200 rounded">Settings</a>
                </li>
              </ul>
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1 p-8">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-lg">Todo App / Todos</h2>
              <div className="w-8 h-8 rounded-full overflow-hidden">
                {useAuth().user?.profile_picture ? (
                  <ProfileImage
                    imageUrl={api.getProfilePictureUrl(useAuth().user.profile_picture)}
                    initials={useAuth().user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  />
                ) : (
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    {useAuth().user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                )}
              </div>
            </div>

            {error && (
              <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
                Error: {error}
              </div>
            )}

            {/* Add Todo Section */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h3 className="text-lg font-medium mb-4">Add Todo</h3>
              <TodoForm
                onSubmit={handleAddTodo}
                submitLabel="Create Todo"
              />
            </div>

            {/* Filters and Your Todos Section */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Filters Section */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium mb-4">Filters</h3>
                  <div className="space-y-2">
                    <button
                      className={`w-full text-left p-2 rounded ${filter === 'all' ? 'bg-gray-100' : 'hover:bg-gray-100'}`}
                      onClick={() => setFilter('all')}
                    >
                      All
                    </button>
                    <button
                      className={`w-full text-left p-2 rounded ${filter === 'active' ? 'bg-gray-100' : 'hover:bg-gray-100'}`}
                      onClick={() => setFilter('active')}
                    >
                      Active
                    </button>
                    <button
                      className={`w-full text-left p-2 rounded ${filter === 'completed' ? 'bg-gray-100' : 'hover:bg-gray-100'}`}
                      onClick={() => setFilter('completed')}
                    >
                      Completed
                    </button>
                  </div>
                </div>
              </div>

              {/* Your Todos Section */}
              <div className="lg:col-span-3">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium mb-4">Your Todos ({filteredTodos.length})</h3>
                  <TodoList
                    todos={filteredTodos}
                    onToggle={handleToggleTodo}
                    onUpdate={handleUpdateTodo}
                    onDelete={handleDeleteTodo}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </ProtectedRoute>

      {/* Floating Chat Widget - Always visible regardless of auth status */}
      <FloatingChatWidget />
    </div>
  );
}
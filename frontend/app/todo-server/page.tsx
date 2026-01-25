import { getTodos } from '@/actions/todoActions';
import TodoListServer from '@/components/TodoListServer';
import TodoFormServer from '@/components/TodoFormServer';

export default async function TodoServerPage() {
  const { success, data: todos, error } = await getTodos();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="py-8">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-center text-gray-800 mb-8">Todo App (Server Components)</h1>

          {error && (
            <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
              Error: {error}
            </div>
          )}

          <TodoFormServer />

          {success && todos && (
            <TodoListServer todos={todos} />
          )}
        </div>
      </div>
    </div>
  );
}
// For creating a new todo
export interface CreateTodoRequest {
  title: string;
}

// For updating an existing todo
export interface UpdateTodoRequest {
  title?: string;
  completed?: boolean;
}

// For API responses
export interface TodoApiResponse {
  data: Todo | Todo[];
  message: string;
}

export interface Todo {
  id: string;              // Unique identifier for each task
  title: string;           // Task description/title
  description?: string;    // Optional task description
  completed: boolean;      // Status indicating whether the task is completed (default: false)
}

export interface TodoFormProps {
  onSubmit: (title: string) => void;
  initialTitle?: string;
  submitLabel: string;
  onCancel?: () => void;
}

export interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onUpdate: (id: string, title: string) => void;
  onDelete: (id: string) => void;
  onEditStart?: (id: string) => void;
}

export interface TodoListProps {
  todos: Todo[];
  onToggle: (id: string) => void;
  onUpdate: (id: string, title: string) => void;
  onDelete: (id: string) => void;
  emptyMessage?: string;
}
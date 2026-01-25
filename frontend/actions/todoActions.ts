'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';

// Type definitions for our API responses
interface ApiResponse<T> {
  data: T | null;
  message: string;
}

interface Todo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
}

interface CreateTodoRequest {
  title: string;
  description?: string;
  completed?: boolean;
}

interface UpdateTodoRequest {
  title?: string;
  description?: string;
  completed?: boolean;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001/api/v1";

// Helper function to get auth token from cookies
const getAuthToken = () => {
  const cookieStore = cookies();
  return cookieStore.get('auth_token')?.value;
};

// Helper function to make authenticated API requests
const makeApiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> => {
  const token = getAuthToken();

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;

    // Redirect to login if unauthorized
    if (response.status === 401) {
      redirect('/login');
    }

    throw new Error(errorMessage);
  }

  return response.json();
};

// Server Action: Get all todos
export async function getTodos(): Promise<{ success: boolean; data?: Todo[]; error?: string }> {
  try {
    const result = await makeApiRequest<Todo[]>('/todos', {
      method: 'GET',
    });

    return { success: true, data: result.data as Todo[] };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error.message : 'Failed to fetch todos' };
  }
}

// Server Action: Create a new todo
export async function createTodo(
  prevState: { success: boolean; error?: string },
  formData: FormData
): Promise<{ success: boolean; error?: string }> {
  try {
    const title = formData.get('title') as string;
    const description = formData.get('description') as string | null;
    const completed = formData.get('completed') === 'true';

    const requestData: CreateTodoRequest = { title };

    if (description) requestData.description = description;
    if (completed !== undefined) requestData.completed = completed;

    await makeApiRequest('/todos', {
      method: 'POST',
      body: JSON.stringify(requestData),
    });

    revalidatePath('/');
    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to create todo'
    };
  }
}

// Server Action: Update a todo
export async function updateTodo(
  id: string,
  prevState: { success: boolean; error?: string },
  formData: FormData
): Promise<{ success: boolean; error?: string }> {
  try {
    const title = formData.get('title') as string;
    const description = formData.get('description') as string | null;
    const completed = formData.get('completed') === 'true';

    const requestData: UpdateTodoRequest = {};

    if (title) requestData.title = title;
    if (description) requestData.description = description;
    if (completed !== undefined) requestData.completed = completed;

    await makeApiRequest(`/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(requestData),
    });

    revalidatePath('/');
    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to update todo'
    };
  }
}

// Server Action: Delete a todo
export async function deleteTodo(
  id: string
): Promise<{ success: boolean; error?: string }> {
  try {
    await makeApiRequest(`/todos/${id}`, {
      method: 'DELETE',
    });

    revalidatePath('/');
    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to delete todo'
    };
  }
}

// Server Action: Toggle todo completion status
export async function toggleTodoCompletion(
  id: string,
  completed: boolean
): Promise<{ success: boolean; error?: string }> {
  try {
    await makeApiRequest(`/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ completed: !completed }),
    });

    revalidatePath('/');
    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to toggle todo completion'
    };
  }
}
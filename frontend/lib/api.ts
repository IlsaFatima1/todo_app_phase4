import { Todo, CreateTodoRequest, UpdateTodoRequest, TodoApiResponse } from '@/types/todo';

// API functions for connecting to the Python backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7860";

// Function to add headers to requests
const getHeaders = (includeAuth: boolean = true): { [key: string]: string } => {
  const headers: { [key: string]: string } = {
    'Content-Type': 'application/json',
  };

  if (includeAuth) {
    // Get token from localStorage
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
  }

  return headers;
};

// API functions that connect to the Python backend
export const api = {
  // Get all todos
  getTodos: async (): Promise<TodoApiResponse> => {
    console.log('DEBUG: Calling getTodos API');
    const response = await fetch(`${API_BASE_URL}/todos`, {
      method: 'GET',
      headers: getHeaders(),
    });

    console.log('DEBUG: getTodos response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      // Handle both standard FastAPI error format and custom format
      const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;

      console.log('DEBUG: getTodos error:', errorMessage);

      // If it's an authentication error (401), we might want to handle it differently
      if (response.status === 401) {
        // Optionally clear the stored token if it's invalid
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      }

      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('DEBUG: getTodos success, data:', data);
    return {
      data: data.data,
      message: data.message
    };
  },

  // Create a new todo
  createTodo: async (request: CreateTodoRequest): Promise<TodoApiResponse> => {
    console.log('DEBUG: Calling createTodo API with request:', request);
    const response = await fetch(`${API_BASE_URL}/todos`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(request),
    });

    console.log('DEBUG: createTodo response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      // Handle both standard FastAPI error format and custom format
      const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;

      console.log('DEBUG: createTodo error:', errorMessage);

      // If it's an authentication error (401), we might want to handle it differently
      if (response.status === 401) {
        // Optionally clear the stored token if it's invalid
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      }

      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('DEBUG: createTodo success, data:', data);
    return {
      data: data.data,
      message: data.message
    };
  },

  // Update an existing todo
  updateTodo: async (id: string, request: UpdateTodoRequest): Promise<TodoApiResponse> => {
    console.log(`DEBUG: Calling updateTodo API for ID: ${id} with request:`, request);
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(request),
    });

    console.log(`DEBUG: updateTodo response status:`, response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      // Handle both standard FastAPI error format and custom format
      const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;

      console.log('DEBUG: updateTodo error:', errorMessage);

      // If it's an authentication error (401), we might want to handle it differently
      if (response.status === 401) {
        // Optionally clear the stored token if it's invalid
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      }

      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('DEBUG: updateTodo success, data:', data);
    return {
      data: data.data,
      message: data.message
    };
  },

  // Delete a todo
  deleteTodo: async (id: string): Promise<TodoApiResponse> => {
    console.log(`DEBUG: Calling deleteTodo API for ID: ${id}`);
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });

    console.log(`DEBUG: deleteTodo response status:`, response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      // Handle both standard FastAPI error format and custom format
      const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;

      console.log('DEBUG: deleteTodo error:', errorMessage);

      // If it's an authentication error (401), we might want to handle it differently
      if (response.status === 401) {
        // Optionally clear the stored token if it's invalid
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      }

      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('DEBUG: deleteTodo success, data:', data);
    return {
      data: data.data,
      message: data.message
    };
  },

  // Update user profile
  updateProfile: async (name: string, email: string): Promise<any> => {
    console.log('DEBUG: Calling updateProfile API with name:', name, 'email:', email);

    const formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);

    // For form data with authentication, we need to include the token in the headers
    // but let the browser set the Content-Type header automatically
    const token = localStorage.getItem('auth_token');
    const headers: { [key: string]: string } = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/auth/update_profile`, {
      method: 'POST',
      headers: headers,
      // For form data, we don't set Content-Type header manually as it will be set automatically
      body: formData,
    });

    console.log('DEBUG: updateProfile response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      // Handle both standard FastAPI error format and custom format
      const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;

      console.log('DEBUG: updateProfile error:', errorMessage);

      // If it's an authentication error (401), we might want to handle it differently
      if (response.status === 401) {
        // Optionally clear the stored token if it's invalid
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      }

      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('DEBUG: updateProfile success, data:', data);
    return {
      data: data.data,
      message: data.message
    };
  },

  // Update user profile picture
  updateProfilePicture: async (file: File): Promise<any> => {
    console.log('DEBUG: Calling updateProfilePicture API with file:', file.name);

    const formData = new FormData();
    formData.append('profile_picture', file);

    // For form data with authentication, we need to include the token in the headers
    // but let the browser set the Content-Type header automatically
    const token = localStorage.getItem('auth_token');
    const headers: { [key: string]: string } = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/auth/update_profile_picture`, {
      method: 'POST',
      headers: headers,
      // For form data, we don't set Content-Type header manually as it will be set automatically
      body: formData,
    });

    console.log('DEBUG: updateProfilePicture response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      // Handle both standard FastAPI error format and custom format
      const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;

      console.log('DEBUG: updateProfilePicture error:', errorMessage);

      // If it's an authentication error (401), we might want to handle it differently
      if (response.status === 401) {
        // Optionally clear the stored token if it's invalid
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      }

      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('DEBUG: updateProfilePicture success, data:', data);
    return {
      data: data.data,
      message: data.message
    };
  },

  // Get profile picture URL
  getProfilePictureUrl: (filename: string): string => {
    // Return the full URL to the backend's user image endpoint
    return `${API_BASE_URL.replace('/api/v1', '')}/api/user_images/${filename}`;
  },

  // Chat with the AI agent
  chatWithAgent: async (message: string, userId: string, conversationId?: string): Promise<any> => {
    console.log('DEBUG: Calling chatWithAgent API with message:', message, 'userId:', userId, 'conversationId:', conversationId);

    // Construct the base URL by removing /api/v1 from the end if it exists
    const baseUrl = API_BASE_URL.endsWith('/api/v1') ?
      API_BASE_URL.substring(0, API_BASE_URL.lastIndexOf('/api/v1')) :
      API_BASE_URL;

    const response = await fetch(`${baseUrl}/api/ai/process_message`, {
      method: 'POST',
      headers: getHeaders(true), // Include auth headers for this endpoint
      body: JSON.stringify({
        message,
        user_id: userId,  // Still pass user_id for compatibility, though backend will use auth
        conversation_id: conversationId || null
      }),
    });

    console.log('DEBUG: chatWithAgent response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      // Handle both standard FastAPI error format and custom format
      const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;

      console.log('DEBUG: chatWithAgent error:', errorMessage);

      // If it's an authentication error (401), we might want to handle it differently
      if (response.status === 401) {
        // Optionally clear the stored token if it's invalid
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      }

      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('DEBUG: chatWithAgent success, data:', data);
    return data;
  },
};


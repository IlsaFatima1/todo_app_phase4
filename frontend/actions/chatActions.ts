'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';

// Type definitions for our API responses
interface ChatResponse {
  success: boolean;
  data?: {
    response: string;
    conversation_id: string;
    tool_calls?: any[];
    timestamp: string;
  };
  message: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

// Helper function to make API requests to the AI endpoint
const makeChatApiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<ChatResponse> => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const errorMessage = errorData.detail || errorData.message || `HTTP error! status: ${response.status}`;

    throw new Error(errorMessage);
  }

  return response.json();
};

// Server Action: Send a message to the AI agent
export async function sendMessageToAgent(
  prevState: { success: boolean; response?: string; error?: string },
  formData: FormData
): Promise<{ success: boolean; response?: string; conversationId?: string; error?: string; toolCalls?: any[] }> {
  try {
    const message = formData.get('message') as string;
    const userId = formData.get('user_id') as string;
    const conversationId = formData.get('conversation_id') as string | null;

    if (!message || !userId) {
      return {
        success: false,
        error: 'Message and user ID are required'
      };
    }

    const response = await makeChatApiRequest('/api/ai/process_message', {
      method: 'POST',
      body: JSON.stringify({
        message,
        user_id: userId,
        conversation_id: conversationId || null
      }),
    });

    if (!response.success) {
      return {
        success: false,
        error: response.message || 'Failed to get response from AI agent'
      };
    }

    revalidatePath('/chat');

    return {
      success: true,
      response: response.data?.response,
      conversationId: response.data?.conversation_id,
      toolCalls: response.data?.tool_calls
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to send message to AI agent'
    };
  }
}

// Server Action: Initialize a new conversation
export async function initializeConversation(userId: string): Promise<{ success: boolean; conversationId?: string; error?: string }> {
  try {
    const response = await makeChatApiRequest('/api/ai/init_conversation', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId
      }),
    });

    if (!response.success) {
      return {
        success: false,
        error: response.message || 'Failed to initialize conversation'
      };
    }

    return {
      success: true,
      conversationId: response.data?.conversation_id
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to initialize conversation'
    };
  }
}

// Server Action: Get conversation history (placeholder)
export async function getConversationHistory(conversationId: string): Promise<{ success: boolean; messages?: any[]; error?: string }> {
  // This is a placeholder - the actual backend may not have this endpoint yet
  // For now, we'll return an empty array to avoid errors
  return {
    success: true,
    messages: []
  };
}
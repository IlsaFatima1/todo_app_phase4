import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ChatPage from '../../frontend/app/chat/page';

// Mock the API client
vi.mock('@/lib/api', () => ({
  api: {
    chatWithAgent: vi.fn(),
  },
}));

// Mock the auth context
vi.mock('@/context/auth-context', () => ({
  useAuth: vi.fn(() => ({
    user: { id: '1', name: 'Test User' },
    isAuthenticated: true,
    logout: vi.fn(),
  })),
}));

describe('ChatPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the chat interface', () => {
    render(<ChatPage />);

    expect(screen.getByText('Todo AI Assistant')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByText('Send')).toBeInTheDocument();
  });

  it('allows user to type and send a message', async () => {
    const { chatWithAgent } = require('@/lib/api');
    chatWithAgent.mockResolvedValue({
      success: true,
      data: {
        response: 'Hello! I received your message.',
        conversation_id: 'test-conversation-id',
        timestamp: new Date().toISOString(),
      },
      message: 'Success',
    });

    render(<ChatPage />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'Hello, AI!' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(chatWithAgent).toHaveBeenCalledWith('Hello, AI!', '1', undefined);
    });
  });

  it('displays user and AI messages', async () => {
    const { chatWithAgent } = require('@/lib/api');
    chatWithAgent.mockResolvedValue({
      success: true,
      data: {
        response: 'Hello! I received your message.',
        conversation_id: 'test-conversation-id',
        timestamp: new Date().toISOString(),
      },
      message: 'Success',
    });

    render(<ChatPage />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
      expect(screen.getByText('Hello! I received your message.')).toBeInTheDocument();
    });
  });

  it('shows loading state while waiting for response', async () => {
    const { chatWithAgent } = require('@/lib/api');
    const promise = new Promise(() => {}); // Never resolving promise for testing
    chatWithAgent.mockReturnValue(promise);

    render(<ChatPage />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    // Check for loading indicator
    expect(screen.getByText('Send')).toBeDisabled();
    // Additional loading state checks would go here
  });

  it('handles API errors gracefully', async () => {
    const { chatWithAgent } = require('@/lib/api');
    chatWithAgent.mockRejectedValue(new Error('API Error'));

    render(<ChatPage />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
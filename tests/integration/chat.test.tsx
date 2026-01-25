import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
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

describe('Chat Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('full conversation flow works correctly', async () => {
    const { chatWithAgent } = require('@/lib/api');

    // Mock responses for different user inputs
    chatWithAgent.mockImplementation((message: string) => {
      if (message.includes('add task')) {
        return Promise.resolve({
          success: true,
          data: {
            response: 'Task "buy groceries" has been added successfully.',
            conversation_id: 'test-conversation-id',
            tool_calls: [{
              name: 'add_task',
              arguments: { title: 'buy groceries', description: '' }
            }],
            timestamp: new Date().toISOString(),
          },
          message: 'Success',
        });
      } else if (message.includes('list tasks')) {
        return Promise.resolve({
          success: true,
          data: {
            response: 'You have 1 pending task: buy groceries',
            conversation_id: 'test-conversation-id',
            tool_calls: [{
              name: 'list_tasks',
              arguments: { status: 'pending' }
            }],
            timestamp: new Date().toISOString(),
          },
          message: 'Success',
        });
      } else {
        return Promise.resolve({
          success: true,
          data: {
            response: 'I understand. How else can I help you?',
            conversation_id: 'test-conversation-id',
            timestamp: new Date().toISOString(),
          },
          message: 'Success',
        });
      }
    });

    render(<ChatPage />);

    // Simulate adding a task
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'Add a task to buy groceries' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/buy groceries/i)).toBeInTheDocument();
      expect(screen.getByText(/Task "buy groceries" has been added/i)).toBeInTheDocument();
    });

    // Simulate listing tasks
    fireEvent.change(input, { target: { value: 'Show me my pending tasks' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/You have 1 pending task/i)).toBeInTheDocument();
    });
  });

  it('maintains conversation history', async () => {
    const { chatWithAgent } = require('@/lib/api');
    chatWithAgent.mockResolvedValue({
      success: true,
      data: {
        response: 'I received your message.',
        conversation_id: 'test-conversation-id',
        timestamp: new Date().toISOString(),
      },
      message: 'Success',
    });

    render(<ChatPage />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    // Send first message
    fireEvent.change(input, { target: { value: 'First message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('First message')).toBeInTheDocument();
      expect(screen.getByText('I received your message.')).toBeInTheDocument();
    });

    // Send second message
    fireEvent.change(input, { target: { value: 'Second message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Second message')).toBeInTheDocument();
      // Both messages should be visible
      expect(screen.getAllByText('I received your message.').length).toBe(2);
    });
  });

  it('displays tool execution results properly', async () => {
    const { chatWithAgent } = require('@/lib/api');
    chatWithAgent.mockResolvedValue({
      success: true,
      data: {
        response: 'Task completed successfully',
        conversation_id: 'test-conversation-id',
        tool_calls: [{
          name: 'complete_task',
          arguments: { id: '123', title: 'Buy groceries' }
        }],
        timestamp: new Date().toISOString(),
      },
      message: 'Success',
    });

    render(<ChatPage />);

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(input, { target: { value: 'Complete task 123' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Task completed successfully/)).toBeInTheDocument();
      expect(screen.getByText(/Tools executed:/)).toBeInTheDocument();
      expect(screen.getByText(/complete_task/)).toBeInTheDocument();
    });
  });

  it('handles error states gracefully', async () => {
    const { chatWithAgent } = require('@/lib/api');
    chatWithAgent.mockRejectedValue(new Error('API unavailable'));

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
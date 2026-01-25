'use client';

import React, { useState } from 'react';
import { TodoItemProps } from '@/types/todo';

const TodoItem: React.FC<TodoItemProps> = ({
  todo,
  onToggle,
  onUpdate,
  onDelete,
  onEditStart
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [isToggling, setIsToggling] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleEdit = () => {
    setIsEditing(true);
    if (onEditStart) {
      onEditStart(todo.id);
    }
  };

  const handleSave = async () => {
    if (editTitle.trim() && editTitle.trim() !== todo.title) {
      setIsUpdating(true);
      try {
        await onUpdate(todo.id, editTitle.trim());
      } finally {
        setIsUpdating(false);
      }
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(todo.title);
    setIsEditing(false);
  };

  const handleToggle = async () => {
    setIsToggling(true);
    try {
      await onToggle(todo.id);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(todo.id);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      handleCancel();
    } else if (e.key === 'Enter') {
      handleSave();
    }
  };

  return (
    <div className={`flex flex-col p-3 mb-2 rounded-lg border ${todo.completed ? 'bg-green-50' : 'bg-white'} shadow-sm`} role="listitem">
      {/* Task ID and title row */}
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center flex-1">
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={handleToggle}
            disabled={isToggling}
            className={`h-5 w-5 rounded focus:ring-blue-500 ${isToggling ? 'text-gray-400' : 'text-blue-600'}`}
            aria-label={todo.completed ? `Mark ${todo.title} as incomplete` : `Mark ${todo.title} as complete`}
          />
          {isEditing ? (
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus
              disabled={isUpdating}
              className={`ml-3 flex-1 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${isUpdating ? 'bg-gray-100' : ''}`}
              aria-label="Edit task"
            />
          ) : (
            <span
              className={`ml-3 flex-1 ${todo.completed ? 'line-through text-gray-500' : 'text-gray-800'}`}
              aria-label={todo.title}
            >
              {todo.title}
            </span>
          )}
        </div>
        <div className="ml-2 text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          ID: {todo.id}
        </div>
      </div>

      {/* Task description below */}
      {todo.description && (
        <div className="text-sm text-gray-600 ml-8 mb-2 pl-2 border-l-2 border-gray-300">
          {todo.description}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex justify-end">
        <div className="flex space-x-2">
          {isEditing ? (
            <>
              <button
                onClick={handleSave}
                disabled={isUpdating}
                className={`px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-green-500 ${isUpdating ? 'bg-green-400 text-gray-200 cursor-not-allowed' : 'bg-green-500 text-white hover:bg-green-600'}`}
                aria-label="Save changes"
              >
                {isUpdating ? 'Saving...' : 'Save'}
              </button>
              <button
                onClick={handleCancel}
                disabled={isUpdating}
                className={`px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-gray-500 ${isUpdating ? 'bg-gray-400 text-gray-200 cursor-not-allowed' : 'bg-gray-500 text-white hover:bg-gray-600'}`}
                aria-label="Cancel editing"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleEdit}
                disabled={isUpdating}
                className={`px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-yellow-500 ${isUpdating ? 'bg-yellow-400 text-gray-200 cursor-not-allowed' : 'bg-yellow-500 text-white hover:bg-yellow-600'}`}
                aria-label={`Edit ${todo.title}`}
              >
                Edit
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className={`px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-red-500 ${isDeleting ? 'bg-red-400 text-gray-200 cursor-not-allowed' : 'bg-red-500 text-white hover:bg-red-600'}`}
                aria-label={`Delete ${todo.title}`}
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TodoItem;
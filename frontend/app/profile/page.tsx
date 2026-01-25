'use client';

import { useState, useEffect, useRef } from 'react';
import { Todo } from '@/types/todo';
import { api } from '@/lib/api';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import FloatingChatWidget from '@/components/FloatingChatWidget';
import { useAuth } from '@/context/auth-context';

export default function ProfilePage() {
  const { user, login } = useAuth();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(user?.name || '');
  const [editEmail, setEditEmail] = useState(user?.email || '');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchTodos = async () => {
      try {
        const response = await api.getTodos();
        setTodos(response.data as Todo[]);
      } catch (err) {
        console.error('Error fetching todos:', err);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchTodos();
    }
  }, [user]);

  // Update edit fields when user data changes
  useEffect(() => {
    if (user) {
      setEditName(user.name || '');
      setEditEmail(user.email || '');
    }
  }, [user]);

  // Calculate stats based on todos
  const totalTasks = todos.length;
  const completedTasks = todos.filter(todo => todo.completed).length;
  const activeTasks = todos.filter(todo => !todo.completed).length;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const handleEditClick = () => {
    setIsEditing(true);
    setError('');
    setSuccess('');
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setError('');
    setSuccess('');
    // Reset to original values
    setEditName(user?.name || '');
    setEditEmail(user?.email || '');
  };

  const handleSaveProfile = async () => {
    if (!editName.trim() || !editEmail.trim()) {
      setError('Name and email are required');
      return;
    }

    try {
      setLoading(true);
      const response = await api.updateProfile(editName, editEmail);

      // Update the auth context with new user data
      // Get the current token from localStorage since update_profile endpoint doesn't return a new one
      const currentToken = localStorage.getItem('auth_token');
      if (currentToken) {
        login(currentToken, response.data);
      }

      setSuccess('Profile updated successfully!');
      setIsEditing(false);
      setError('');
    } catch (err) {
      console.error('Error updating profile:', err);
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const ChangeProfilePictureButtonComponent = () => {
    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState('');
    const [uploadSuccess, setUploadSuccess] = useState('');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      // Validate file type
      if (!file.type.startsWith('image/')) {
        setUploadError('Please select a valid image file (JPEG, PNG, GIF)');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setUploadError('File size exceeds 5MB limit');
        return;
      }

      try {
        setIsUploading(true);
        setUploadError('');

        const response = await api.updateProfilePicture(file);

        // Update the auth context with new user data
        const currentToken = localStorage.getItem('auth_token');
        if (currentToken) {
          login(currentToken, response.data);
        }

        setUploadSuccess('Profile picture updated successfully!');
        setTimeout(() => setUploadSuccess(''), 5000); // Clear success message after 5 seconds
      } catch (err) {
        console.error('Error uploading profile picture:', err);
        setUploadError(err instanceof Error ? err.message : 'Failed to upload profile picture');
      } finally {
        setIsUploading(false);
        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
    };

    const handleClick = () => {
      if (fileInputRef.current) {
        fileInputRef.current.click();
      }
    };

    return (
      <div className="mt-4">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/*"
          className="hidden"
        />
        <button
          className={`px-4 py-2 rounded ${
            isUploading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-purple-500 hover:bg-purple-600'
          } text-white`}
          onClick={handleClick}
          disabled={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Change Photo'}
        </button>
        {uploadError && (
          <div className="mt-2 text-red-500 text-sm">{uploadError}</div>
        )}
        {uploadSuccess && (
          <div className="mt-2 text-green-500 text-sm">{uploadSuccess}</div>
        )}
      </div>
    );
  };

  const ProfileImage = ({ imageUrl, initials }: { imageUrl: string; initials: string }) => {
    const [hasError, setHasError] = useState(false);

    if (hasError) {
      return (
        <div className="w-full h-full bg-blue-500 rounded-full flex items-center justify-center text-white text-xl font-bold">
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
                  <a href="/todos" className="flex items-center p-2 hover:bg-gray-200 rounded">Todos</a>
                </li>
                <li>
                  <a href="/profile" className="flex items-center p-2 bg-gray-200 rounded">Profile</a>
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
              <h2 className="text-lg">Todo App / Profile</h2>
              <div className="w-8 h-8 rounded-full overflow-hidden">
                {user?.profile_picture ? (
                  <ProfileImage
                    imageUrl={api.getProfilePictureUrl(user.profile_picture)}
                    initials={user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  />
                ) : (
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                )}
              </div>
            </div>

            {/* Profile Header Card */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              {error && (
                <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
                  Error: {error}
                </div>
              )}
              {success && (
                <div className="mb-4 p-4 bg-green-100 text-green-700 rounded-lg">
                  {success}
                </div>
              )}
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-16 h-16 rounded-full flex items-center justify-center text-white text-xl font-bold mr-4 overflow-hidden">
                    {user?.profile_picture ? (
                      <ProfileImage
                        imageUrl={api.getProfilePictureUrl(user.profile_picture)}
                        initials={user?.name?.charAt(0)?.toUpperCase() || 'U'}
                      />
                    ) : (
                      <div className="w-full h-full bg-blue-500 rounded-full flex items-center justify-center text-white text-xl font-bold">
                        {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                      </div>
                    )}
                  </div>
                  {isEditing ? (
                    <div className="flex-1">
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="w-full text-xl font-medium mb-2 p-2 border border-gray-300 rounded"
                        placeholder="Enter your name"
                      />
                      <input
                        type="email"
                        value={editEmail}
                        onChange={(e) => setEditEmail(e.target.value)}
                        className="w-full text-gray-600 p-2 border border-gray-300 rounded"
                        placeholder="Enter your email"
                      />
                    </div>
                  ) : (
                    <div>
                      <h3 className="text-xl font-medium">{user?.name || 'User Name'}</h3>
                      <p className="text-gray-600">{user?.email || 'user@example.com'}</p>
                    </div>
                  )}
                </div>
                <div className="flex flex-col items-center">
                  {isEditing ? (
                    <div className="flex flex-col items-center">
                      <button
                        className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 mb-2"
                        onClick={handleCancelEdit}
                      >
                        Cancel
                      </button>
                      <button
                        className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                        onClick={handleSaveProfile}
                      >
                        Save
                      </button>
                    </div>
                  ) : (
                    <>
                      <button
                        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mb-2"
                        onClick={handleEditClick}
                      >
                        Edit Profile
                      </button>
                      <ChangeProfilePictureButtonComponent />
                    </>
                  )}
                </div>
              </div>
            </div>


            {/* Activity Statistics Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h4 className="text-gray-500 text-sm mb-1">Total Tasks</h4>
                <p className="text-2xl font-bold">{totalTasks}</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h4 className="text-gray-500 text-sm mb-1">Completed Tasks</h4>
                <p className="text-2xl font-bold">{completedTasks}</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h4 className="text-gray-500 text-sm mb-1">Completion Rate</h4>
                <p className="text-2xl font-bold">{completionRate}%</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h4 className="text-gray-500 text-sm mb-1">Active Tasks</h4>
                <p className="text-2xl font-bold">{activeTasks}</p>
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
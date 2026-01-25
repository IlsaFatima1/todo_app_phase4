'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import FloatingChatWidget from '@/components/FloatingChatWidget';
import { useAuth } from '@/context/auth-context';
import { api } from '@/lib/api';

export default function SettingsPage() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('light');
  const { user, logout } = useAuth(); // Destructure user from auth context

  // Initialize settings from localStorage or default values
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'system' | null;

    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  // Apply theme changes
  useEffect(() => {
    localStorage.setItem('theme', theme);

    // Remove all theme classes first
    document.documentElement.classList.remove('light', 'dark');

    // Apply the current theme
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else if (theme === 'light') {
      document.documentElement.classList.add('light');
    } else {
      // For system theme, check user's system preference
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (systemPrefersDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.add('light');
      }
    }
  }, [theme]);

  const handleThemeChange = (selectedTheme: 'light' | 'dark' | 'system') => {
    setTheme(selectedTheme);
  };

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      if (theme === 'system') {
        if (e.matches) {
          document.documentElement.classList.add('dark');
          document.documentElement.classList.remove('light');
        } else {
          document.documentElement.classList.add('light');
          document.documentElement.classList.remove('dark');
        }
      }
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);

    return () => {
      mediaQuery.removeEventListener('change', handleSystemThemeChange);
    };
  }, [theme]);

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
                  <a href="/profile" className="flex items-center p-2 hover:bg-gray-200 rounded">Profile</a>
                </li>
                <li>
                  <a href="/settings" className="flex items-center p-2 bg-gray-200 rounded">Settings</a>
                </li>
              </ul>
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1 p-8">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-lg">Todo App / Settings</h2>
            </div>


            {/* Theme Selection */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h3 className="text-lg font-medium mb-4">Theme Selection</h3>
              <div className="space-y-3">
                <div className="flex items-center p-3 rounded-lg border hover:bg-gray-50 cursor-pointer" onClick={() => handleThemeChange('light')}>
                  <input
                    type="radio"
                    id="light-theme"
                    name="theme"
                    className="mr-3"
                    checked={theme === 'light'}
                    onChange={() => handleThemeChange('light')}
                  />
                  <label htmlFor="light-theme" className="flex-1 cursor-pointer">
                    <div className="font-medium">Light Theme</div>
                    <div className="text-sm text-gray-500">Clean, bright interface with light backgrounds</div>
                  </label>
                  <div className="w-8 h-8 rounded-full bg-white border-2 border-gray-300 flex items-center justify-center">
                    <div className="w-4 h-4 rounded-full bg-gray-300"></div>
                  </div>
                </div>

                <div className="flex items-center p-3 rounded-lg border hover:bg-gray-50 cursor-pointer" onClick={() => handleThemeChange('dark')}>
                  <input
                    type="radio"
                    id="dark-theme"
                    name="theme"
                    className="mr-3"
                    checked={theme === 'dark'}
                    onChange={() => handleThemeChange('dark')}
                  />
                  <label htmlFor="dark-theme" className="flex-1 cursor-pointer">
                    <div className="font-medium">Dark Theme</div>
                    <div className="text-sm text-gray-500">Comfortable low-light interface with dark backgrounds</div>
                  </label>
                  <div className="w-8 h-8 rounded-full bg-gray-800 border-2 border-gray-600 flex items-center justify-center">
                    <div className="w-4 h-4 rounded-full bg-gray-400"></div>
                  </div>
                </div>

                <div className="flex items-center p-3 rounded-lg border hover:bg-gray-50 cursor-pointer" onClick={() => handleThemeChange('system')}>
                  <input
                    type="radio"
                    id="system-theme"
                    name="theme"
                    className="mr-3"
                    checked={theme === 'system'}
                    onChange={() => handleThemeChange('system')}
                  />
                  <label htmlFor="system-theme" className="flex-1 cursor-pointer">
                    <div className="font-medium">System Theme</div>
                    <div className="text-sm text-gray-500">Automatically adjusts to your system preferences</div>
                  </label>
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-800 to-gray-300 border-2 border-gray-400 flex items-center justify-center">
                    <div className="w-4 h-4 rounded-full bg-gray-500"></div>
                  </div>
                </div>
              </div>

              <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
                <div className="flex items-start">
                  <div className="flex-shrink-0 mt-1">
                    <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-blue-700">
                      <strong>Current theme:</strong> {theme === 'light' ? 'Light' : theme === 'dark' ? 'Dark' : 'System (follows your device settings)'}
                    </p>
                  </div>
                </div>
              </div>
            </div>


            {/* Logout Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium mb-4">Account</h3>
              <button
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                onClick={() => {
                  logout();
                  window.location.href = '/landing';
                }}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </ProtectedRoute>

      {/* Floating Chat Widget - Always visible regardless of auth status */}
      <FloatingChatWidget />
    </div>
  );
}
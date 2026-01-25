'use client';

import Link from 'next/link';
import { useAuth } from '@/context/auth-context';

export default function LandingPage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Top Navigation */}
      <nav className="flex items-center justify-between p-6">
        <div className="text-2xl font-bold text-gray-800">TaskFlow Pro</div>
        <div className="flex space-x-4">
          <Link href="/login">
            <button className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              Login
            </button>
          </Link>
          <Link href="/register">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Sign Up
            </button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex flex-col items-center justify-center py-20 px-4">
        <div className="max-w-3xl text-center">
          <h1 className="text-5xl font-extrabold text-gray-900 mb-6">
            Master Your Productivity with Smart Task Management
          </h1>
          <p className="text-xl text-gray-600 mb-10">
            Elevate your workflow with intelligent task organization. Focus on what matters, achieve more with precision and clarity.
          </p>
          {!user ? (
            <Link href="/login">
              <button className="px-8 py-4 bg-blue-600 text-white text-lg font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-lg">
                Get Started
              </button>
            </Link>
          ) : (
            <Link href="/todos">
              <button className="px-8 py-4 bg-blue-600 text-white text-lg font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-lg">
                Go to Dashboard
              </button>
            </Link>
          )}
        </div>
      </main>
    </div>
  );
}
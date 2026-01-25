'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/auth-context';

export default function HomePage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        // Redirect to landing page if not authenticated
        router.push('/landing');
      } else {
        // Redirect to todos page if authenticated
        router.push('/todos');
      }
    }
  }, [user, authLoading, router]);

  // While redirecting, show a simple loading indicator
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  );
}
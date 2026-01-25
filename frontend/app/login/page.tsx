'use client';

import LoginForm from '@/components/auth/LoginForm';
import { useAuth } from '@/context/auth-context';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  // Redirect to todos page if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/todos');
    }
  }, [isAuthenticated, router]);

  if (isAuthenticated) {
    return null; // Or a loading component while redirecting
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <LoginForm />
    </div>
  );
}
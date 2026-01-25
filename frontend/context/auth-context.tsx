"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Define the shape of our auth context
interface AuthContextType {
  user: any | null;
  token: string | null;
  loading: boolean;
  login: (token: string, userData: any) => void;
  logout: () => void;
  register: (name: string, email: string, password: string) => Promise<void>;
  isAuthenticated: boolean;
}

// Create the context with default values
const AuthContext = createContext<AuthContextType>(undefined!);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Check for existing token in localStorage on mount
  useEffect(() => {
    console.log('DEBUG: AuthContext - Checking for existing tokens in localStorage');
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');

    console.log('DEBUG: AuthContext - Stored token exists:', !!storedToken);
    console.log('DEBUG: AuthContext - Stored user exists:', !!storedUser);

    if (storedToken && storedUser) {
      setToken(storedToken);
      const parsedUser = JSON.parse(storedUser);
      setUser(parsedUser);
      console.log('DEBUG: AuthContext - Loaded user from localStorage:', parsedUser);
    } else {
      console.log('DEBUG: AuthContext - No existing tokens found');
    }
    setLoading(false);
    console.log('DEBUG: AuthContext - Setting loading to false');
  }, []);

  const login = (token: string, userData: any) => {
    console.log('DEBUG: AuthContext - Login called with token:', token, 'and userData:', userData);
    // The backend returns the token and user data directly after login
    setToken(token);
    setUser(userData);
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_user', JSON.stringify(userData));
    console.log('DEBUG: AuthContext - Token and user stored in localStorage');
  };

  const register = async (name: string, email: string, password: string) => {
    console.log('DEBUG: AuthContext - Register called with name:', name, 'email:', email);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      console.log('DEBUG: AuthContext - Register response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.log('DEBUG: AuthContext - Register error response:', errorData);
        throw new Error(errorData.message || 'Registration failed');
      }

      const data = await response.json();
      console.log('DEBUG: AuthContext - Register success response:', data);
      const { data: authData, message } = data;

      if (authData && authData.access_token) {
        setToken(authData.access_token);
        setUser(authData.user);
        localStorage.setItem('auth_token', authData.access_token);
        localStorage.setItem('auth_user', JSON.stringify(authData.user));
        console.log('DEBUG: AuthContext - Registration tokens stored in localStorage');
      }
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = () => {
    console.log('DEBUG: AuthContext - Logout called');
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    console.log('DEBUG: AuthContext - Tokens cleared from localStorage');
  };

  const isAuthenticated = !!token;

  const contextValue: AuthContextType = {
    user,
    token,
    loading,
    login,
    logout,
    register,
    isAuthenticated,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
import React, { createContext, useContext, useEffect, useState } from 'react';
import { authApi, getAccessToken, getCurrentUserId, setAccessToken, setCurrentUserId } from '@/api/client';
import { useNavigate } from 'react-router-dom';

interface AuthContextValue {
    userId: number | null;
    accessToken: string | null;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, username: string, password: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const navigate = useNavigate();
    const [accessToken, setAccessTokenState] = useState<string | null>(null);
    const [userId, setUserIdState] = useState<number | null>(null);

    useEffect(() => {
        const token = getAccessToken();
        const id = getCurrentUserId();
        setAccessTokenState(token);
        setUserIdState(id);
    }, []);

    const login = async (email: string, password: string) => {
        const res = await authApi.login({ email, password });
        // authApi stores tokens in localStorage; read them
        const token = getAccessToken();
        const id = getCurrentUserId();
        setAccessTokenState(token);
        setUserIdState(id);
        // navigate to dashboard
        navigate('/');
    };

    const register = async (email: string, username: string, password: string) => {
        const res = await authApi.register({ email, username, password });
        const token = getAccessToken();
        const id = getCurrentUserId();
        setAccessTokenState(token);
        setUserIdState(id);
        navigate('/');
    };

    const logout = () => {
        setAccessToken(null);
        setCurrentUserId(null);
        setAccessTokenState(null);
        setUserIdState(null);
        navigate('/login');
    };

    return (
        <AuthContext.Provider value={{ userId, accessToken, isAuthenticated: !!accessToken, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
}

export default AuthContext;

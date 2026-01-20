import React, { createContext, useContext, useEffect, useState } from 'react';
import { authApi, getAccessToken, getCurrentUserId, setAccessToken, setCurrentUserId, getCurrentUserRole, setCurrentUserRole } from '@/api/client';
import { useNavigate } from 'react-router-dom';

interface AuthContextValue {
    userId: number | null;
    role: string | null;
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
    const [role, setRoleState] = useState<string | null>(null);

    useEffect(() => {
        const token = getAccessToken();
        const id = getCurrentUserId();
        const r = getCurrentUserRole();
        setAccessTokenState(token);
        setUserIdState(id);
        setRoleState(r);
    }, []);

    const login = async (email: string, password: string) => {
        const res = await authApi.login({ email, password });
        // authApi stores tokens in localStorage; read them
        const token = getAccessToken();
        const id = getCurrentUserId();
        const r = getCurrentUserRole();
        setAccessTokenState(token);
        setUserIdState(id);
        setRoleState(r);
        // navigate to dashboard
        navigate('/');
    };

    const register = async (email: string, username: string, password: string) => {
        const res = await authApi.register({ email, username, password });
        const token = getAccessToken();
        const id = getCurrentUserId();
        const r = getCurrentUserRole();
        setAccessTokenState(token);
        setUserIdState(id);
        setRoleState(r);
        navigate('/');
    };

    const logout = () => {
        setAccessToken(null);
        setCurrentUserId(null);
        setCurrentUserRole(null);
        setAccessTokenState(null);
        setUserIdState(null);
        setRoleState(null);
        navigate('/login');
    };

    return (
        <AuthContext.Provider value={{ userId, role, accessToken, isAuthenticated: !!accessToken, login, register, logout }}>
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

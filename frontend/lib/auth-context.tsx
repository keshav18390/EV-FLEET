"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { api, friendlyError } from "./api";
import type { User } from "./types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string, role: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const stored = localStorage.getItem("ev_fleet_user");
    const token = localStorage.getItem("ev_fleet_token");
    if (stored && token) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        // ignore parse error, treat as logged out
      }
    }
    setLoading(false);
  }, []);

  async function login(email: string, password: string) {
    try {
      const resp = await api.post("/api/auth/login", { email, password });
      localStorage.setItem("ev_fleet_token", resp.data.access_token);
      localStorage.setItem("ev_fleet_user", JSON.stringify(resp.data.user));
      setUser(resp.data.user);
      router.push("/dashboard");
    } catch (err) {
      throw new Error(friendlyError(err));
    }
  }

  async function register(fullName: string, email: string, password: string, role: string) {
    try {
      const resp = await api.post("/api/auth/register", { full_name: fullName, email, password, role });
      localStorage.setItem("ev_fleet_token", resp.data.access_token);
      localStorage.setItem("ev_fleet_user", JSON.stringify(resp.data.user));
      setUser(resp.data.user);
      router.push("/dashboard");
    } catch (err) {
      throw new Error(friendlyError(err));
    }
  }

  function logout() {
    localStorage.removeItem("ev_fleet_token");
    localStorage.removeItem("ev_fleet_user");
    setUser(null);
    router.push("/login");
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

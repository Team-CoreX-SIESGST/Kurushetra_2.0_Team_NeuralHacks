"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { registerUser } from "@/services/auth/authServices";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Restore user/token immediately for smoother UI
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    } catch {
      localStorage.removeItem("user");
    }
    checkAuth();
  }, []);

  // Keep multiple tabs in sync
  useEffect(() => {
    const onStorage = (e) => {
      if (e.key === "user" || e.key === "token") {
        const token = localStorage.getItem("token");
        const storedUser = localStorage.getItem("user");
        if (!token) {
          setUser(null);
          return;
        }
        try {
          setUser(storedUser ? JSON.parse(storedUser) : null);
        } catch {
          localStorage.removeItem("user");
          setUser(null);
        }
      }
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setUser(null);
        localStorage.removeItem("user");
        return;
      }

      const response = await fetch("/api/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await response.json().catch(() => null);

      if (response.ok) {
        // Some backends return {user: {...}}, others return {...user fields}
        const userData = data?.user ?? data;
        if (userData) {
          setUser(userData);
          localStorage.setItem("user", JSON.stringify(userData));
        } else {
          // If response shape is unexpected, keep token-based auth but clear bad user
          localStorage.removeItem("user");
          setUser(null);
        }
      } else {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setUser(null);
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // Support both shapes: { token, user } or { token, userData }
        const userData = data?.user ?? data?.userData ?? null;
        localStorage.setItem("token", data.token);
        if (userData) {
          setUser(userData);
          localStorage.setItem("user", JSON.stringify(userData));
        } else {
          // If API doesn't return user, fetch it now
          await checkAuth();
        }
        return { success: true };
      } else {
        return { success: false, error: data?.message || "Login failed" };
      }
    } catch (error) {
      return { success: false, error: "Login failed" };
    }
  };

  const register = async (userData) => {
    try {
      const response = await registerUser(userData);
      console.log(response);
      return { success: true };
    } catch (error) {
      return { success: false, error: "Registration failed" };
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    router.push("/login");
  };

  const sendOTP = async (email) => {
    try {
      const response = await fetch("/api/auth/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await response.json();
      return response.ok
        ? { success: true, message: data.message }
        : { success: false, error: data.message };
    } catch {
      return { success: false, error: "Failed to send OTP" };
    }
  };

  const verifyOTP = async (email, otp) => {
    try {
      const response = await fetch("/api/auth/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp }),
      });
      const data = await response.json();
      return response.ok
        ? { success: true, message: data.message }
        : { success: false, error: data.message };
    } catch {
      return { success: false, error: "OTP verification failed" };
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    sendOTP,
    verifyOTP,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

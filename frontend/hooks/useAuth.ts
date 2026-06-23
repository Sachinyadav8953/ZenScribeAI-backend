"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { authService } from "@/services/authService";
import { LoginRequest, RegisterRequest } from "@/types";
import { getErrorMessage } from "@/lib/utils";

export function useAuth() {
  const { user, isAuthenticated, setAuth, logout: storeLogout, setUser } = useAuthStore();
  const router = useRouter();

  const login = useCallback(
    async (data: LoginRequest) => {
      const tokens = await authService.login(data);
      // fetch user profile after login
      const me = await authService.getMe();
      setAuth(me, tokens);
      router.push("/dashboard");
    },
    [setAuth, router]
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      await authService.register(data);
      router.push("/login");
    },
    [router]
  );

  const logout = useCallback(() => {
    storeLogout();
    router.push("/login");
  }, [storeLogout, router]);

  const refreshUser = useCallback(async () => {
    try {
      const me = await authService.getMe();
      setUser(me);
    } catch (e) {
      console.error(getErrorMessage(e));
    }
  }, [setUser]);

  return { user, isAuthenticated, login, register, logout, refreshUser };
}

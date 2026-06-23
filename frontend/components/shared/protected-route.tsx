"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import { useAuthStore } from "@/stores/authStore";
import { authService } from "@/services/authService";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, setUser, setAuth, initFromCookies } = useAuthStore();

  useEffect(() => {
    const token = Cookies.get("access_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    initFromCookies();
    // Hydrate user from API
    authService.getMe().then(setUser).catch(() => {
      router.replace("/login");
    });
  }, []);

  return <>{children}</>;
}

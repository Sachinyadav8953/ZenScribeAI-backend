"use client";

import { create } from "zustand";
import Cookies from "js-cookie";
import { User, TokenResponse } from "@/types";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, tokens: TokenResponse) => void;
  setUser: (user: User) => void;
  logout: () => void;
  initFromCookies: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,

  setAuth: (user, tokens) => {
    Cookies.set("access_token", tokens.access_token, {
      expires: 1,
      sameSite: "strict",
    });
    Cookies.set("refresh_token", tokens.refresh_token, {
      expires: 7,
      sameSite: "strict",
    });
    set({ user, accessToken: tokens.access_token, isAuthenticated: true });
  },

  setUser: (user) => set({ user }),

  logout: () => {
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");
    set({ user: null, accessToken: null, isAuthenticated: false });
  },

  initFromCookies: () => {
    const token = Cookies.get("access_token");
    if (token) {
      set({ accessToken: token, isAuthenticated: true });
    }
  },
}));

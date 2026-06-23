import apiClient from "@/lib/axios";
import { LoginRequest, RegisterRequest, TokenResponse, User } from "@/types";

export const authService = {
  async login(data: LoginRequest): Promise<TokenResponse> {
    const res = await apiClient.post<TokenResponse>("/auth/login", data);
    return res.data;
  },

  async register(data: RegisterRequest): Promise<User> {
    const res = await apiClient.post<User>("/auth/register", data);
    return res.data;
  },

  async forgotPassword(email: string): Promise<{ message: string }> {
    const res = await apiClient.post("/auth/forgot-password", { email });
    return res.data;
  },

  async resetPassword(token: string, new_password: string): Promise<{ message: string }> {
    const res = await apiClient.post("/auth/reset-password", { token, new_password });
    return res.data;
  },

  async getMe(): Promise<User> {
    const res = await apiClient.get<User>("/auth/me");
    return res.data;
  },
};

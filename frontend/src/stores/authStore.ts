import { create } from "zustand";

import apiClient from "../services/apiClient";
import type { User } from "../types";

interface AuthState {
  currentUser: User | null;
  authToken: string | null;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  fetchCurrentUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  currentUser: null,
  authToken: localStorage.getItem("authToken"),
  isLoading: false,

  login: (token: string) => {
    localStorage.setItem("authToken", token);
    set({ authToken: token });
  },

  logout: () => {
    localStorage.removeItem("authToken");
    set({ authToken: null, currentUser: null });
  },

  fetchCurrentUser: async () => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get<User>("/auth/user/");
      set({ currentUser: response.data, isLoading: false });
    } catch (error) {
      console.error("Failed to fetch current user:", error);
      set({ isLoading: false });
    }
  },
}));

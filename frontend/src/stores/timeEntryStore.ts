import { create } from "zustand";

import apiClient from "../services/apiClient";
import type { PaginatedResponse, TimeEntry } from "../types";
import type { CrudState } from "./createCrudStore";

interface TimeEntryExtraState {
  recentEntries: TimeEntry[];
  fetchRecent: (limit?: number) => Promise<void>;
}

type TimeEntryState = CrudState<TimeEntry> & TimeEntryExtraState;

export const useTimeEntryStore = create<TimeEntryState>((set, get) => ({
  // CrudState implementation
  records: [],
  isLoading: false,

  fetch: async () => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get<PaginatedResponse<TimeEntry>>("/time-entries/");
      const records = response.data.results;
      set({ records, isLoading: false });
    } catch (error) {
      console.error("Failed to fetch time entries:", error);
      set({ isLoading: false });
    }
  },

  create: async (data: Partial<TimeEntry>) => {
    set({ isLoading: true });
    try {
      const response = await apiClient.post<TimeEntry>("/time-entries/", data);
      const newRecord = response.data;
      // Add to the beginning of the list (most recent first)
      const records = [newRecord, ...get().records];
      const recentEntries = [newRecord, ...get().recentEntries].slice(0, 10);
      set({
        records,
        recentEntries,
        isLoading: false,
      });
      return newRecord;
    } catch (error) {
      console.error("Failed to create time entry:", error);
      set({ isLoading: false });
      throw error;
    }
  },

  update: async (id: number, data: Partial<TimeEntry>) => {
    set({ isLoading: true });
    try {
      const response = await apiClient.patch<TimeEntry>(`/time-entries/${id}/`, data);
      const updatedRecord = response.data;
      const records = get().records.map((r) => (r.id === id ? updatedRecord : r));
      const recentEntries = get().recentEntries.map((r) => (r.id === id ? updatedRecord : r));
      set({
        records,
        recentEntries,
        isLoading: false,
      });
      return updatedRecord;
    } catch (error) {
      console.error("Failed to update time entry:", error);
      set({ isLoading: false });
      throw error;
    }
  },

  delete: async (id: number) => {
    set({ isLoading: true });
    try {
      await apiClient.delete(`/time-entries/${id}/`);
      const records = get().records.filter((r) => r.id !== id);
      const recentEntries = get().recentEntries.filter((r) => r.id !== id);
      set({
        records,
        recentEntries,
        isLoading: false,
      });
    } catch (error) {
      console.error("Failed to delete time entry:", error);
      set({ isLoading: false });
      throw error;
    }
  },

  // Extra state implementation
  recentEntries: [],

  fetchRecent: async (limit = 10) => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get<PaginatedResponse<TimeEntry>>(
        `/time-entries/?ordering=-start_time&limit=${limit}`
      );
      const recentEntries = response.data.results;
      set({ recentEntries, isLoading: false });
    } catch (error) {
      console.error("Failed to fetch recent time entries:", error);
      set({ isLoading: false });
    }
  },
}));

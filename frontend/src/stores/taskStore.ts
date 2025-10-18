import { create } from "zustand";

import apiClient from "../services/apiClient";
import type { PaginatedResponse, Task } from "../types";
import type { CrudState } from "./createCrudStore";

interface TaskFilterState {
  filteredRecords: Task[];
  filterByProject: (projectId: number | null) => void;
  filterByTags: (tagIds: number[]) => void;
  clearFilters: () => void;
}

type TaskState = CrudState<Task> & TaskFilterState;

export const useTaskStore = create<TaskState>((set, get) => ({
  // CrudState implementation
  records: [],
  isLoading: false,

  fetch: async () => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get<PaginatedResponse<Task>>("/tasks/");
      const records = response.data.results;
      set({ records, filteredRecords: records, isLoading: false });
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
      set({ isLoading: false });
    }
  },

  create: async (data: Partial<Task>) => {
    set({ isLoading: true });
    try {
      const response = await apiClient.post<Task>("/tasks/", data);
      const newRecord = response.data;
      const records = [...get().records, newRecord];
      set({
        records,
        filteredRecords: records,
        isLoading: false,
      });
      return newRecord;
    } catch (error) {
      console.error("Failed to create task:", error);
      set({ isLoading: false });
      throw error;
    }
  },

  update: async (id: number, data: Partial<Task>) => {
    set({ isLoading: true });
    try {
      const response = await apiClient.patch<Task>(`/tasks/${id}/`, data);
      const updatedRecord = response.data;
      const records = get().records.map((r) => (r.id === id ? updatedRecord : r));
      const filteredRecords = get().filteredRecords.map((r) => (r.id === id ? updatedRecord : r));
      set({
        records,
        filteredRecords,
        isLoading: false,
      });
      return updatedRecord;
    } catch (error) {
      console.error("Failed to update task:", error);
      set({ isLoading: false });
      throw error;
    }
  },

  delete: async (id: number) => {
    set({ isLoading: true });
    try {
      await apiClient.delete(`/tasks/${id}/`);
      const records = get().records.filter((r) => r.id !== id);
      const filteredRecords = get().filteredRecords.filter((r) => r.id !== id);
      set({
        records,
        filteredRecords,
        isLoading: false,
      });
    } catch (error) {
      console.error("Failed to delete task:", error);
      set({ isLoading: false });
      throw error;
    }
  },

  // Filter state implementation
  filteredRecords: [],

  filterByProject: (projectId: number | null) => {
    const { records } = get();
    const filteredRecords = records.filter((task) => task.project === projectId);
    set({ filteredRecords });
  },

  filterByTags: (tagIds: number[]) => {
    const { records } = get();
    if (tagIds.length === 0) {
      set({ filteredRecords: records });
      return;
    }
    const filteredRecords = records.filter((task) =>
      tagIds.every((tagId) => task.tags.includes(tagId))
    );
    set({ filteredRecords });
  },

  clearFilters: () => {
    const { records } = get();
    set({ filteredRecords: records });
  },
}));

import { create } from "zustand";

import apiClient from "../services/apiClient";
import type { PaginatedResponse } from "../types";

export interface CrudState<T> {
  records: T[];
  isLoading: boolean;
  fetch: () => Promise<void>;
  create: (data: Partial<T>) => Promise<T>;
  update: (id: number, data: Partial<T>) => Promise<T>;
  delete: (id: number) => Promise<void>;
}

export function createCrudStore<T extends { id: number }>(endpoint: string) {
  return create<CrudState<T>>((set, get) => ({
    records: [],
    isLoading: false,

    fetch: async () => {
      set({ isLoading: true });
      try {
        const response = await apiClient.get<PaginatedResponse<T>>(`/${endpoint}/`);
        set({ records: response.data.results, isLoading: false });
      } catch (error) {
        console.error(`Failed to fetch ${endpoint}:`, error);
        set({ isLoading: false });
      }
    },

    create: async (data: Partial<T>) => {
      set({ isLoading: true });
      try {
        const response = await apiClient.post<T>(`/${endpoint}/`, data);
        const newRecord = response.data;
        set({
          records: [...get().records, newRecord],
          isLoading: false,
        });
        return newRecord;
      } catch (error) {
        console.error(`Failed to create ${endpoint}:`, error);
        set({ isLoading: false });
        throw error;
      }
    },

    update: async (id: number, data: Partial<T>) => {
      set({ isLoading: true });
      try {
        const response = await apiClient.patch<T>(`/${endpoint}/${id}/`, data);
        const updatedRecord = response.data;
        set({
          records: get().records.map((r) => (r.id === id ? updatedRecord : r)),
          isLoading: false,
        });
        return updatedRecord;
      } catch (error) {
        console.error(`Failed to update ${endpoint}:`, error);
        set({ isLoading: false });
        throw error;
      }
    },

    delete: async (id: number) => {
      set({ isLoading: true });
      try {
        await apiClient.delete(`/${endpoint}/${id}/`);
        set({
          records: get().records.filter((r) => r.id !== id),
          isLoading: false,
        });
      } catch (error) {
        console.error(`Failed to delete ${endpoint}:`, error);
        set({ isLoading: false });
        throw error;
      }
    },
  }));
}

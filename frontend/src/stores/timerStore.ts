import { create } from "zustand";

import type { ActiveTimer } from "../types";

interface TimerState {
  isRunning: boolean;
  elapsedSeconds: number;
  activeTimer: ActiveTimer | null;
  updateElapsed: (seconds: number) => void;
  setActiveTimer: (timer: ActiveTimer | null) => void;
  setIsRunning: (isRunning: boolean) => void;
  reset: () => void;
}

export const useTimerStore = create<TimerState>((set) => ({
  isRunning: false,
  elapsedSeconds: 0,
  activeTimer: null,

  updateElapsed: (seconds: number) => {
    set({ elapsedSeconds: seconds });
  },

  setActiveTimer: (timer: ActiveTimer | null) => {
    set({ activeTimer: timer, isRunning: timer !== null });
  },

  setIsRunning: (isRunning: boolean) => {
    set({ isRunning });
  },

  reset: () => {
    set({
      isRunning: false,
      elapsedSeconds: 0,
      activeTimer: null,
    });
  },
}));

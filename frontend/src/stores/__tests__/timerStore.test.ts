import { beforeEach, describe, expect, it } from "vitest";

import type { ActiveTimer } from "../../types";
import { useTimerStore } from "../timerStore";

describe("timerStore", () => {
  beforeEach(() => {
    // Clear store state before each test
    useTimerStore.setState({
      isRunning: false,
      elapsedSeconds: 0,
      activeTimer: null,
    });
  });

  it("should initialize with default values", () => {
    const state = useTimerStore.getState();
    expect(state.isRunning).toBe(false);
    expect(state.elapsedSeconds).toBe(0);
    expect(state.activeTimer).toBeNull();
  });

  it("should update elapsed seconds", () => {
    const { updateElapsed } = useTimerStore.getState();

    updateElapsed(120);

    const state = useTimerStore.getState();
    expect(state.elapsedSeconds).toBe(120);
  });

  it("should set active timer", () => {
    const { setActiveTimer } = useTimerStore.getState();

    const activeTimer: ActiveTimer = {
      taskId: 1,
      startTime: "2025-10-18T09:00:00Z",
    };

    setActiveTimer(activeTimer);

    const state = useTimerStore.getState();
    expect(state.activeTimer).toEqual(activeTimer);
    expect(state.isRunning).toBe(true);
  });

  it("should set active timer to null and stop running", () => {
    const { setActiveTimer } = useTimerStore.getState();

    // First set an active timer
    setActiveTimer({
      taskId: 1,
      startTime: "2025-10-18T09:00:00Z",
    });

    expect(useTimerStore.getState().isRunning).toBe(true);

    // Then set to null
    setActiveTimer(null);

    const state = useTimerStore.getState();
    expect(state.activeTimer).toBeNull();
    expect(state.isRunning).toBe(false);
  });

  it("should set isRunning", () => {
    const { setIsRunning } = useTimerStore.getState();

    setIsRunning(true);
    expect(useTimerStore.getState().isRunning).toBe(true);

    setIsRunning(false);
    expect(useTimerStore.getState().isRunning).toBe(false);
  });

  it("should reset timer state", () => {
    const { setActiveTimer, updateElapsed, reset } = useTimerStore.getState();

    // Set some state
    setActiveTimer({
      taskId: 1,
      startTime: "2025-10-18T09:00:00Z",
    });
    updateElapsed(300);

    expect(useTimerStore.getState().isRunning).toBe(true);
    expect(useTimerStore.getState().elapsedSeconds).toBe(300);
    expect(useTimerStore.getState().activeTimer).not.toBeNull();

    // Reset
    reset();

    const state = useTimerStore.getState();
    expect(state.isRunning).toBe(false);
    expect(state.elapsedSeconds).toBe(0);
    expect(state.activeTimer).toBeNull();
  });

  it("should handle timer with no task (task-less timer)", () => {
    const { setActiveTimer } = useTimerStore.getState();

    const activeTimer: ActiveTimer = {
      taskId: null,
      startTime: "2025-10-18T09:00:00Z",
    };

    setActiveTimer(activeTimer);

    const state = useTimerStore.getState();
    expect(state.activeTimer?.taskId).toBeNull();
    expect(state.isRunning).toBe(true);
  });

  it("should update elapsed seconds multiple times", () => {
    const { updateElapsed } = useTimerStore.getState();

    updateElapsed(10);
    expect(useTimerStore.getState().elapsedSeconds).toBe(10);

    updateElapsed(20);
    expect(useTimerStore.getState().elapsedSeconds).toBe(20);

    updateElapsed(30);
    expect(useTimerStore.getState().elapsedSeconds).toBe(30);
  });

  it("should allow starting a new timer while one is running", () => {
    const { setActiveTimer } = useTimerStore.getState();

    // Start first timer
    const firstTimer: ActiveTimer = {
      taskId: 1,
      startTime: "2025-10-18T09:00:00Z",
    };
    setActiveTimer(firstTimer);

    expect(useTimerStore.getState().activeTimer?.taskId).toBe(1);

    // Start second timer (simulating switching tasks)
    const secondTimer: ActiveTimer = {
      taskId: 2,
      startTime: "2025-10-18T10:00:00Z",
    };
    setActiveTimer(secondTimer);

    const state = useTimerStore.getState();
    expect(state.activeTimer?.taskId).toBe(2);
    expect(state.isRunning).toBe(true);
  });
});

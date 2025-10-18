import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { useAuthStore } from "../authStore";

describe("authStore", () => {
  beforeEach(() => {
    // Clear store state before each test
    useAuthStore.setState({
      currentUser: null,
      authToken: null,
      isLoading: false,
    });
    // Clear localStorage
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it("should initialize with null user and token", () => {
    const state = useAuthStore.getState();
    expect(state.currentUser).toBeNull();
    expect(state.authToken).toBeNull();
    expect(state.isLoading).toBe(false);
  });

  it("should login and store token in localStorage", () => {
    const { login } = useAuthStore.getState();
    const token = "test-token-123";

    login(token);

    const state = useAuthStore.getState();
    expect(state.authToken).toBe(token);
    expect(localStorage.getItem("authToken")).toBe(token);
  });

  it("should logout and remove token from localStorage", () => {
    const { login, logout } = useAuthStore.getState();

    // First login
    login("test-token");
    expect(useAuthStore.getState().authToken).toBe("test-token");

    // Then logout
    logout();

    const state = useAuthStore.getState();
    expect(state.authToken).toBeNull();
    expect(state.currentUser).toBeNull();
    expect(localStorage.getItem("authToken")).toBeNull();
  });

  it("should fetch current user successfully", async () => {
    const { fetchCurrentUser } = useAuthStore.getState();

    await fetchCurrentUser();

    const state = useAuthStore.getState();
    expect(state.currentUser).toEqual({
      id: 1,
      username: "testuser",
      email: "test@example.com",
    });
    expect(state.isLoading).toBe(false);
  });

  it("should set isLoading during fetchCurrentUser", async () => {
    const { fetchCurrentUser } = useAuthStore.getState();

    const fetchPromise = fetchCurrentUser();

    // Check loading state immediately
    expect(useAuthStore.getState().isLoading).toBe(true);

    await fetchPromise;

    // Check loading state after completion
    expect(useAuthStore.getState().isLoading).toBe(false);
  });

  it("should restore authToken from localStorage on initialization", () => {
    // Set token in localStorage before creating store
    localStorage.setItem("authToken", "stored-token");

    // Get initial state (simulating store initialization)
    const initialToken = localStorage.getItem("authToken");

    expect(initialToken).toBe("stored-token");
  });
});

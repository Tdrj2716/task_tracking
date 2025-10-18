import { beforeEach, describe, expect, it } from "vitest";

import { useTimeEntryStore } from "../timeEntryStore";

describe("timeEntryStore", () => {
  beforeEach(() => {
    // Clear store state before each test
    useTimeEntryStore.setState({
      records: [],
      recentEntries: [],
      isLoading: false,
    });
  });

  it("should initialize with empty records", () => {
    const state = useTimeEntryStore.getState();
    expect(state.records).toEqual([]);
    expect(state.recentEntries).toEqual([]);
    expect(state.isLoading).toBe(false);
  });

  it("should fetch time entries successfully", async () => {
    const { fetch } = useTimeEntryStore.getState();

    await fetch();

    const state = useTimeEntryStore.getState();
    expect(state.records).toHaveLength(2);
    expect(state.records[0].task).toBe(1);
    expect(state.records[1].task).toBe(2);
    expect(state.isLoading).toBe(false);
  });

  it("should create a new time entry and add to beginning", async () => {
    const { create } = useTimeEntryStore.getState();

    const newEntry = await create({
      task: 1,
      start_time: "2025-10-03T09:00:00Z",
      end_time: "2025-10-03T10:00:00Z",
      duration_seconds: 3600,
    });

    const state = useTimeEntryStore.getState();
    expect(newEntry.task).toBe(1);
    expect(state.records).toHaveLength(1);
    expect(state.records[0]).toEqual(newEntry); // New entry is at the beginning
    expect(state.recentEntries).toHaveLength(1);
  });

  it("should update a time entry", async () => {
    const { fetch, update } = useTimeEntryStore.getState();

    // First fetch entries
    await fetch();

    // Then update the first entry
    const updatedEntry = await update(1, { duration_seconds: 7200 });

    const state = useTimeEntryStore.getState();
    expect(updatedEntry.duration_seconds).toBe(7200);
    expect(state.records[0].duration_seconds).toBe(7200);
  });

  it("should delete a time entry", async () => {
    const { fetch, delete: deleteEntry } = useTimeEntryStore.getState();

    // First fetch entries
    await fetch();
    expect(useTimeEntryStore.getState().records).toHaveLength(2);

    // Then delete the first entry
    await deleteEntry(1);

    const state = useTimeEntryStore.getState();
    expect(state.records).toHaveLength(1);
    expect(state.records[0].id).toBe(2);
  });

  it("should fetch recent entries with default limit", async () => {
    const { fetchRecent } = useTimeEntryStore.getState();

    await fetchRecent();

    const state = useTimeEntryStore.getState();
    expect(state.recentEntries).toHaveLength(2);
    expect(state.isLoading).toBe(false);
  });

  it("should fetch recent entries with custom limit", async () => {
    const { fetchRecent } = useTimeEntryStore.getState();

    await fetchRecent(1);

    const state = useTimeEntryStore.getState();
    expect(state.recentEntries).toHaveLength(1);
  });

  it("should limit recentEntries to 10 items when creating", async () => {
    const { create } = useTimeEntryStore.getState();

    // Create 12 entries
    for (let i = 0; i < 12; i++) {
      await create({
        task: 1,
        start_time: `2025-10-${String(i + 1).padStart(2, "0")}T09:00:00Z`,
        end_time: `2025-10-${String(i + 1).padStart(2, "0")}T10:00:00Z`,
        duration_seconds: 3600,
      });
    }

    const state = useTimeEntryStore.getState();
    expect(state.records).toHaveLength(12); // All entries in records
    expect(state.recentEntries).toHaveLength(10); // Limited to 10 in recentEntries
  });

  it("should update recentEntries when updating an entry", async () => {
    const { fetch, fetchRecent, update } = useTimeEntryStore.getState();

    // Fetch all entries and recent entries
    await fetch();
    await fetchRecent();

    // Update an entry
    await update(1, { duration_seconds: 9999 });

    const state = useTimeEntryStore.getState();
    const recentEntry = state.recentEntries.find((e) => e.id === 1);
    expect(recentEntry?.duration_seconds).toBe(9999);
  });

  it("should remove from both records and recentEntries when deleting", async () => {
    const { fetch, fetchRecent, delete: deleteEntry } = useTimeEntryStore.getState();

    // Fetch all entries and recent entries
    await fetch();
    await fetchRecent();

    expect(useTimeEntryStore.getState().records).toHaveLength(2);
    expect(useTimeEntryStore.getState().recentEntries).toHaveLength(2);

    // Delete an entry
    await deleteEntry(1);

    const state = useTimeEntryStore.getState();
    expect(state.records).toHaveLength(1);
    expect(state.recentEntries).toHaveLength(1);
    expect(state.records.find((e) => e.id === 1)).toBeUndefined();
    expect(state.recentEntries.find((e) => e.id === 1)).toBeUndefined();
  });

  it("should set isLoading during fetch", async () => {
    const { fetch } = useTimeEntryStore.getState();

    const fetchPromise = fetch();

    // Check loading state immediately
    expect(useTimeEntryStore.getState().isLoading).toBe(true);

    await fetchPromise;

    // Check loading state after completion
    expect(useTimeEntryStore.getState().isLoading).toBe(false);
  });
});

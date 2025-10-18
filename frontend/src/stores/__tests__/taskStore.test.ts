import { beforeEach, describe, expect, it } from "vitest";

import { useTaskStore } from "../taskStore";

describe("taskStore", () => {
  beforeEach(() => {
    // Clear store state before each test
    useTaskStore.setState({
      records: [],
      filteredRecords: [],
      isLoading: false,
    });
  });

  it("should initialize with empty records", () => {
    const state = useTaskStore.getState();
    expect(state.records).toEqual([]);
    expect(state.filteredRecords).toEqual([]);
    expect(state.isLoading).toBe(false);
  });

  it("should fetch tasks successfully", async () => {
    const { fetch } = useTaskStore.getState();

    await fetch();

    const state = useTaskStore.getState();
    expect(state.records).toHaveLength(2);
    expect(state.filteredRecords).toHaveLength(2);
    expect(state.records[0].name).toBe("Task 1");
    expect(state.records[1].name).toBe("Task 2");
    expect(state.isLoading).toBe(false);
  });

  it("should create a new task", async () => {
    const { create } = useTaskStore.getState();

    const newTask = await create({
      name: "New Task",
      project: 1,
      parent: null,
      tags: [1],
      estimate_minutes: 45,
    });

    const state = useTaskStore.getState();
    expect(newTask.name).toBe("New Task");
    expect(state.records).toHaveLength(1);
    expect(state.filteredRecords).toHaveLength(1);
    expect(state.records[0]).toEqual(newTask);
  });

  it("should update a task", async () => {
    const { fetch, update } = useTaskStore.getState();

    // First fetch tasks
    await fetch();

    // Then update the first task
    const updatedTask = await update(1, { name: "Updated Task 1" });

    const state = useTaskStore.getState();
    expect(updatedTask.name).toBe("Updated Task 1");
    expect(state.records[0].name).toBe("Updated Task 1");
    expect(state.filteredRecords[0].name).toBe("Updated Task 1");
  });

  it("should delete a task", async () => {
    const { fetch, delete: deleteTask } = useTaskStore.getState();

    // First fetch tasks
    await fetch();
    expect(useTaskStore.getState().records).toHaveLength(2);

    // Then delete the first task
    await deleteTask(1);

    const state = useTaskStore.getState();
    expect(state.records).toHaveLength(1);
    expect(state.filteredRecords).toHaveLength(1);
    expect(state.records[0].id).toBe(2);
  });

  it("should filter tasks by project", async () => {
    const { fetch, filterByProject } = useTaskStore.getState();

    // First fetch tasks
    await fetch();

    // Filter by project 1
    filterByProject(1);

    const state = useTaskStore.getState();
    expect(state.records).toHaveLength(2); // Original records unchanged
    expect(state.filteredRecords).toHaveLength(1); // Only tasks with project 1
    expect(state.filteredRecords[0].project).toBe(1);
  });

  it("should filter tasks by tags", async () => {
    const { fetch, filterByTags } = useTaskStore.getState();

    // First fetch tasks
    await fetch();

    // Filter by tag 1
    filterByTags([1]);

    const state = useTaskStore.getState();
    expect(state.records).toHaveLength(2); // Original records unchanged
    expect(state.filteredRecords).toHaveLength(1); // Only tasks with tag 1
    expect(state.filteredRecords[0].tags).toContain(1);
  });

  it("should clear filters", async () => {
    const { fetch, filterByProject, clearFilters } = useTaskStore.getState();

    // First fetch tasks
    await fetch();

    // Apply filter
    filterByProject(1);
    expect(useTaskStore.getState().filteredRecords).toHaveLength(1);

    // Clear filters
    clearFilters();

    const state = useTaskStore.getState();
    expect(state.filteredRecords).toHaveLength(2); // All tasks visible again
    expect(state.filteredRecords).toEqual(state.records);
  });

  it("should return all tasks when filterByTags is called with empty array", async () => {
    const { fetch, filterByTags } = useTaskStore.getState();

    // First fetch tasks
    await fetch();

    // Filter with empty array
    filterByTags([]);

    const state = useTaskStore.getState();
    expect(state.filteredRecords).toHaveLength(2);
    expect(state.filteredRecords).toEqual(state.records);
  });

  it("should set isLoading during fetch", async () => {
    const { fetch } = useTaskStore.getState();

    const fetchPromise = fetch();

    // Check loading state immediately
    expect(useTaskStore.getState().isLoading).toBe(true);

    await fetchPromise;

    // Check loading state after completion
    expect(useTaskStore.getState().isLoading).toBe(false);
  });
});

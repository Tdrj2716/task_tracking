import { http, HttpResponse } from "msw";

import type { PaginatedResponse, Project, Tag, Task, TimeEntry, User } from "../../types";

const API_URL = "http://localhost:8000/api";

// Mock data
const mockUser: User = {
  id: 1,
  username: "testuser",
  email: "test@example.com",
};

const mockProjects: Project[] = [
  {
    id: 1,
    name: "Project 1",
    color: "#B29632",
    created_at: "2025-10-01T00:00:00Z",
    updated_at: "2025-10-01T00:00:00Z",
  },
  {
    id: 2,
    name: "Project 2",
    color: "#FF5733",
    created_at: "2025-10-02T00:00:00Z",
    updated_at: "2025-10-02T00:00:00Z",
  },
];

const mockTags: Tag[] = [
  { id: 1, name: "Tag 1", created_at: "2025-10-01T00:00:00Z" },
  { id: 2, name: "Tag 2", created_at: "2025-10-02T00:00:00Z" },
];

const mockTasks: Task[] = [
  {
    id: 1,
    name: "Task 1",
    project: 1,
    project_name: "Project 1",
    parent: null,
    parent_name: undefined,
    tags: [1],
    tag_names: ["Tag 1"],
    level: 0,
    root: null,
    estimate_minutes: 60,
    duration_seconds: 0,
    created_at: "2025-10-01T00:00:00Z",
    updated_at: "2025-10-01T00:00:00Z",
  },
  {
    id: 2,
    name: "Task 2",
    project: 2,
    project_name: "Project 2",
    parent: null,
    parent_name: undefined,
    tags: [2],
    tag_names: ["Tag 2"],
    level: 0,
    root: null,
    estimate_minutes: 30,
    duration_seconds: 0,
    created_at: "2025-10-02T00:00:00Z",
    updated_at: "2025-10-02T00:00:00Z",
  },
];

const mockTimeEntries: TimeEntry[] = [
  {
    id: 1,
    task: 1,
    task_name: "Task 1",
    project: 1,
    start_time: "2025-10-01T09:00:00Z",
    end_time: "2025-10-01T10:00:00Z",
    duration_seconds: 3600,
    created_at: "2025-10-01T10:00:00Z",
  },
  {
    id: 2,
    task: 2,
    task_name: "Task 2",
    project: 2,
    start_time: "2025-10-02T09:00:00Z",
    end_time: "2025-10-02T09:30:00Z",
    duration_seconds: 1800,
    created_at: "2025-10-02T09:30:00Z",
  },
];

export const handlers = [
  // Auth endpoints
  http.get(`${API_URL}/auth/user/`, () => {
    return HttpResponse.json(mockUser);
  }),

  // Project endpoints
  http.get(`${API_URL}/projects/`, () => {
    const response: PaginatedResponse<Project> = {
      count: mockProjects.length,
      next: null,
      previous: null,
      results: mockProjects,
    };
    return HttpResponse.json(response);
  }),

  http.post(`${API_URL}/projects/`, async ({ request }) => {
    const body = (await request.json()) as Partial<Project>;
    const newProject: Project = {
      id: mockProjects.length + 1,
      name: body.name!,
      color: body.color || "#B29632",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(newProject, { status: 201 });
  }),

  // Tag endpoints
  http.get(`${API_URL}/tags/`, () => {
    const response: PaginatedResponse<Tag> = {
      count: mockTags.length,
      next: null,
      previous: null,
      results: mockTags,
    };
    return HttpResponse.json(response);
  }),

  // Task endpoints
  http.get(`${API_URL}/tasks/`, () => {
    const response: PaginatedResponse<Task> = {
      count: mockTasks.length,
      next: null,
      previous: null,
      results: mockTasks,
    };
    return HttpResponse.json(response);
  }),

  http.post(`${API_URL}/tasks/`, async ({ request }) => {
    const body = (await request.json()) as Partial<Task>;
    const newTask: Task = {
      id: mockTasks.length + 1,
      name: body.name!,
      project: body.project || null,
      parent: body.parent || null,
      tags: body.tags || [],
      level: body.parent ? 1 : 0,
      root: null,
      estimate_minutes: body.estimate_minutes || null,
      duration_seconds: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(newTask, { status: 201 });
  }),

  http.patch(`${API_URL}/tasks/:id/`, async ({ params, request }) => {
    const { id } = params;
    const body = (await request.json()) as Partial<Task>;
    const task = mockTasks.find((t) => t.id === Number(id));
    if (!task) {
      return new HttpResponse(null, { status: 404 });
    }
    const updatedTask: Task = {
      ...task,
      ...body,
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(updatedTask);
  }),

  http.delete(`${API_URL}/tasks/:id/`, ({ params }) => {
    const { id } = params;
    const task = mockTasks.find((t) => t.id === Number(id));
    if (!task) {
      return new HttpResponse(null, { status: 404 });
    }
    return new HttpResponse(null, { status: 204 });
  }),

  // TimeEntry endpoints
  http.get(`${API_URL}/time-entries/`, ({ request }) => {
    const url = new URL(request.url);
    const limit = url.searchParams.get("limit");
    const results = limit ? mockTimeEntries.slice(0, Number(limit)) : mockTimeEntries;

    const response: PaginatedResponse<TimeEntry> = {
      count: results.length,
      next: null,
      previous: null,
      results,
    };
    return HttpResponse.json(response);
  }),

  http.post(`${API_URL}/time-entries/`, async ({ request }) => {
    const body = (await request.json()) as Partial<TimeEntry>;
    const newEntry: TimeEntry = {
      id: mockTimeEntries.length + 1,
      task: body.task || null,
      task_name: body.task ? `Task ${body.task}` : undefined,
      project: body.project || null,
      start_time: body.start_time!,
      end_time: body.end_time || null,
      duration_seconds: body.duration_seconds || null,
      created_at: new Date().toISOString(),
    };
    return HttpResponse.json(newEntry, { status: 201 });
  }),

  http.patch(`${API_URL}/time-entries/:id/`, async ({ params, request }) => {
    const { id } = params;
    const body = (await request.json()) as Partial<TimeEntry>;
    const entry = mockTimeEntries.find((e) => e.id === Number(id));
    if (!entry) {
      return new HttpResponse(null, { status: 404 });
    }
    const updatedEntry: TimeEntry = {
      ...entry,
      ...body,
    };
    return HttpResponse.json(updatedEntry);
  }),

  http.delete(`${API_URL}/time-entries/:id/`, ({ params }) => {
    const { id } = params;
    const entry = mockTimeEntries.find((e) => e.id === Number(id));
    if (!entry) {
      return new HttpResponse(null, { status: 404 });
    }
    return new HttpResponse(null, { status: 204 });
  }),
];

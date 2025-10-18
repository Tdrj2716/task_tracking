// Domain Models - TypeScript type definitions for API responses

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface Project {
  id: number;
  name: string;
  color: string; // Hex color code (e.g., "#B29632")
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: number;
  name: string;
  created_at: string;
}

export interface Task {
  id: number;
  name: string;
  project: number | null; // Project ID (null for Inbox)
  project_name?: string; // Read-only field from serializer
  parent: number | null; // Parent task ID
  parent_name?: string; // Read-only field from serializer
  tags: number[]; // Array of tag IDs
  tag_names?: string[]; // Read-only field from serializer
  level: number; // 0=root, 1=child, 2=grandchild
  root: number | null; // Root task ID
  estimate_minutes: number | null; // Estimated work time in minutes
  duration_seconds: number; // Actual cumulative work time in seconds
  created_at: string;
  updated_at: string;
}

export interface TimeEntry {
  id: number;
  task: number | null; // Task ID (nullable)
  task_name?: string; // Read-only field from serializer (nullable)
  project: number | null; // Project ID (nullable, auto-inherited from task)
  start_time: string; // ISO 8601 datetime string
  end_time: string | null; // ISO 8601 datetime string (nullable for running timer)
  duration_seconds: number | null; // Duration in seconds (auto-calculated)
  created_at: string;
}

// Client-side models

export interface ActiveTimer {
  taskId: number | null; // Task ID for running timer (null for task-less timer)
  startTime: string; // ISO 8601 datetime string
}

// API Response wrappers

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  status: number;
  message: string;
  data?: unknown;
  originalError?: unknown;
}

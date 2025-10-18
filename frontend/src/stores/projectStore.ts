import type { Project } from "../types";
import { createCrudStore } from "./createCrudStore";

export const useProjectStore = createCrudStore<Project>("projects");

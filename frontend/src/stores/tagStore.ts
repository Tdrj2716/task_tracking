import type { Tag } from "../types";
import { createCrudStore } from "./createCrudStore";

export const useTagStore = createCrudStore<Tag>("tags");

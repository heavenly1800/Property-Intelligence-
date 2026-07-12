import { api } from "../lib/api";

export async function analyzeProperty(input: string) {
  return api.post("/intake", { input });
}

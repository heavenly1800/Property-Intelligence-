import { api } from "../lib/api";

export async function analyzeProperty(input: string) {
  return api("/intake", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      input,
    }),
  });
}
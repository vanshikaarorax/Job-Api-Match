const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");

export type Breakdown = {
  skills: { score: number; max: number; mustHave: { matched: number; total: number }; niceToHave: { matched: number; total: number } };
  experience: { score: number; max: number };
  location: { score: number; max: number; reason: string };
  salary: { score: number; max: number };
};

export type Candidate = { id: number; name: string; skills: string[]; yearsOfExperience: number; location: string; expectedSalary: number };
export type Job = { id: number; title: string };
export type Recommendation = { jobId: number; title: string; score: number; breakdown: Breakdown };
export type Recommendations = { candidateId: number; results: Recommendation[] };

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers: { "Content-Type": "application/json", ...options?.headers } });
  } catch {
    throw new Error("Unable to reach the API. Check that FastAPI is running.");
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: unknown } | null;
    const detail = typeof body?.detail === "string" ? body.detail : "Please check the entered values and try again.";
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api = {
  createCandidate: (payload: Record<string, unknown>) => request<Candidate>("/candidates", { method: "POST", body: JSON.stringify(payload) }),
  createJob: (payload: Record<string, unknown>) => request<Job>("/jobs", { method: "POST", body: JSON.stringify(payload) }),
  recommendations: (candidateId: number, limit: number) => request<Recommendations>(`/candidates/${candidateId}/recommendations?limit=${limit}`),
};

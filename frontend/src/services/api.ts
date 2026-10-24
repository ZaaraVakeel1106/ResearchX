export interface HealthResponse {
  status: "ok";
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }

  const payload: unknown = await response.json();
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("status" in payload) ||
    payload.status !== "ok"
  ) {
    throw new Error("Health check returned an invalid response");
  }

  return payload as HealthResponse;
}

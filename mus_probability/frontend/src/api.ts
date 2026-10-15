import type { CalculateRequest, CalculateResponse } from "./types";

const API_BASE = "http://localhost:8001";

export async function calculate(req: CalculateRequest): Promise<CalculateResponse> {
  const r = await fetch(`${API_BASE}/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(`API error ${r.status}: ${text}`);
  }
  return r.json();
}

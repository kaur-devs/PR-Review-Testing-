import type { Evaluation, Flag } from './types';

const API_BASE = import.meta.env.VITE_API_URL ?? '/api/v1';

function adminHeaders(): Record<string, string> {
  const token = localStorage.getItem('adminToken');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function unwrap<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(body.detail ?? 'Request failed');
  }
  return response.json() as Promise<T>;
}

export async function listFlags(projectKey: string): Promise<Flag[]> {
  const response = await fetch(
    `${API_BASE}/${encodeURIComponent(projectKey)}/flags`,
  );
  return unwrap<Flag[]>(response);
}

export async function createFlag(
  projectKey: string,
  flag: Pick<Flag, 'key' | 'description' | 'enabled' | 'rollout_percent'>,
): Promise<Flag> {
  const response = await fetch(
    `${API_BASE}/${encodeURIComponent(projectKey)}/flags`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...adminHeaders() },
      body: JSON.stringify(flag),
    },
  );
  return unwrap<Flag>(response);
}

export async function evaluateFor(
  projectKey: string,
  userKey: string,
  attributes: Record<string, unknown> = {},
): Promise<Evaluation> {
  const response = await fetch(
    `${API_BASE}/${encodeURIComponent(projectKey)}/evaluate`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_key: userKey, attributes }),
    },
  );
  return unwrap<Evaluation>(response);
}

export interface Schedule {
  id: number;
  apply_at: string;
  ramp_to: number;
  ramp_minutes: number;
}

export async function scheduleChange(
  projectKey: string,
  flagKey: string,
  schedule: { apply_at: string; ramp_to: number; ramp_minutes: number },
): Promise<Schedule> {
  const response = await fetch(
    `${API_BASE}/${encodeURIComponent(projectKey)}/flags/${flagKey}/schedule`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(schedule),
    },
  );
  return unwrap<Schedule>(response);
}

export async function listSchedules(
  projectKey: string,
  flagKey: string,
): Promise<Schedule[]> {
  const flags = await listFlags(projectKey);
  const flag = flags.find((candidate) => candidate.key === flagKey);
  return (flag as any).schedules ?? [];
}

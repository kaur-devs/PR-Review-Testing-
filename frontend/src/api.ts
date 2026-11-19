import type { Evaluation, Flag, History } from './types';

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

export async function listHistory(projectKey: string): Promise<History> {
  const response = await fetch(
    `${API_BASE}/${encodeURIComponent(projectKey)}/history`,
  );
  return unwrap<History>(response);
}

export async function listFlagHistory(
  projectKey: string,
  flagKey: string,
  options: { limit?: number; since?: string } = {},
): Promise<History> {
  const query = new URLSearchParams();
  if (options.limit !== undefined) query.set('limit', String(options.limit));
  if (options.since !== undefined) query.set('since', options.since);

  const response = await fetch(
    `${API_BASE}/${encodeURIComponent(projectKey)}/flags/${flagKey}/history?${query}`,
  );
  return unwrap<History>(response);
}

export async function updateFlag(
  projectKey: string,
  flagKey: string,
  patch: Partial<Pick<Flag, 'description' | 'enabled' | 'rollout_percent'>>,
): Promise<Flag> {
  const response = await fetch(
    `${API_BASE}/${encodeURIComponent(projectKey)}/flags/${flagKey}`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    },
  );
  return unwrap<Flag>(response);
}

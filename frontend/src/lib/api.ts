const API_BASE = '/api/v1';

function getToken(): string | null {
  return localStorage.getItem('token');
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (res.status === 204) {
    return {} as T;
  }

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || 'Error en la solicitud');
  }

  return data as T;
}

// Auth
export const auth = {
  login: (email: string, password: string) =>
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (email: string, password: string, full_name: string, company?: string) =>
    apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name, company }),
    }),
  me: () => apiRequest('/auth/me'),
};

// Accounts
export const accounts = {
  list: () => apiRequest('/accounts'),
  get: (id: number) => apiRequest(`/accounts/${id}`),
  create: (data: any) =>
    apiRequest('/accounts', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: any) =>
    apiRequest(`/accounts/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) =>
    apiRequest(`/accounts/${id}`, { method: 'DELETE' }),
  startWarmup: (id: number) =>
    apiRequest(`/accounts/${id}/start-warmup`, { method: 'POST' }),
  pauseWarmup: (id: number) =>
    apiRequest(`/accounts/${id}/pause-warmup`, { method: 'POST' }),
};

// Campaigns
export const campaigns = {
  list: () => apiRequest('/campaigns'),
  get: (id: number) => apiRequest(`/campaigns/${id}`),
  create: (data: any) =>
    apiRequest('/campaigns', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: number, data: any) =>
    apiRequest(`/campaigns/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: number) =>
    apiRequest(`/campaigns/${id}`, { method: 'DELETE' }),
  launch: (id: number) =>
    apiRequest(`/campaigns/${id}/launch`, { method: 'POST' }),
  pause: (id: number) =>
    apiRequest(`/campaigns/${id}/pause`, { method: 'POST' }),
};

// Analytics
export const analytics = {
  overview: () => apiRequest('/analytics/overview'),
  warmupScores: () => apiRequest('/analytics/warmup-scores'),
  seedTest: (account_id: number, test_email: string) =>
    apiRequest('/analytics/seed-test', {
      method: 'POST',
      body: JSON.stringify({ account_id, test_email }),
    }),
};

// Domains
export const domains = {
  list: () => apiRequest('/domains'),
  create: (domain_name: string) =>
    apiRequest('/domains', { method: 'POST', body: JSON.stringify({ domain_name }) }),
  checkDns: (id: number) =>
    apiRequest(`/domains/${id}/dns-check`),
  delete: (id: number) =>
    apiRequest(`/domains/${id}`, { method: 'DELETE' }),
};

// Warmup
export const warmup = {
  status: () => apiRequest('/warmup/status'),
  schedule: (accountId: number) => apiRequest(`/warmup/${accountId}/schedule`),
};

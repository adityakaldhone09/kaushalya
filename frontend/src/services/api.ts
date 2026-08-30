/**
 * KAUSHALYA API service
 * Direct fetch calls to the FastAPI backend for features not covered
 * by the generated @workspace/api-client-react hooks.
 */

import { getToken } from '@/lib/auth';

const BASE = '/api';

export async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: { message: res.statusText } }));
    throw new Error(err?.error?.message || err?.detail || res.statusText);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Auth API ──────────────────────────────────────────────────────────────────

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  role: string;
  organization?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface GoogleLoginPayload {
  credential: string;
  role?: 'TRAINEE' | 'EMPLOYER' | 'TRAINING_INSTITUTE';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
    organization?: string | null;
  };
}

export const authApi = {
  register: (data: RegisterPayload) =>
    request<AuthResponse>('POST', '/auth/register', data),

  login: (data: LoginPayload) =>
    request<AuthResponse>('POST', '/auth/login', data),

  google: (data: GoogleLoginPayload) =>
    request<AuthResponse>('POST', '/auth/google', data),

  me: () => request<AuthResponse['user']>('GET', '/auth/me'),

  logout: () => request<void>('POST', '/auth/logout'),

  verifyEmail: (token: string) =>
    request<void>('POST', '/auth/verify-email', { token }),

  resendVerification: (email: string) =>
    request<void>('POST', '/auth/resend-verification', { email }),

  forgotPassword: (email: string) =>
    request<void>('POST', '/auth/forgot-password', { email }),

  resetPassword: (data: { token: string; new_password: string }) =>
    request<void>('POST', '/auth/reset-password', data),

  changePassword: (data: { current_password: string; new_password: string }) =>
    request<void>('POST', '/auth/change-password', data),
};

// ── System API ────────────────────────────────────────────────────────────────

export const systemApi = {
  emailStatus: () => request<unknown>('GET', '/system/email-status'),
};

// ── Intelligence API ──────────────────────────────────────────────────────────

export const intelligenceApi = {
  employabilityScore: () =>
    request<{ score: number; classification: string; breakdown: Record<string, number> }>(
      'GET', '/intelligence/employability/me'
    ),

  skillGapMe: (targetRole?: string) =>
    request<{ overall_match: number; target_role: string; matching_skills: string[]; missing_skills: string[]; weak_skills: unknown[]; priority_skills: string[]; recommended_training: string[] }>(
      'GET', `/intelligence/skill-gap/me${targetRole ? `?target_role=${encodeURIComponent(targetRole)}` : ''}`
    ),

  skillGapAnalyze: (target_role: string, target_skills?: string[]) =>
    request('POST', '/intelligence/skill-gap/analyze', { target_role, target_skills }),

  districtDigitalTwin: (district: string) =>
    request('GET', `/intelligence/districts/${encodeURIComponent(district)}/digital-twin`),

  programImpact: () => request('GET', '/intelligence/program-impact'),
  programImpactDetail: (id: string) => request('GET', `/intelligence/program-impact/${id}`),
};


// ── Employment API ────────────────────────────────────────────────────────────

export const employmentApi = {
  myOutcomes: () => request('GET', '/employment/me'),
  create: (data: unknown) => request('POST', '/employment', data),
  update: (id: string, data: unknown) => request('PUT', `/employment/${id}`, data),
};

// ── Certifications & Enrollments ──────────────────────────────────────────────

export const trainingApi = {
  myEnrollments: () => request('GET', '/enrollments/me'),
  enroll: (program_id: string) => request('POST', '/enrollments', { program_id }),
  updateEnrollment: (id: string, status: string) =>
    request('PUT', `/enrollments/${id}`, { status }),
  myCertifications: () => request('GET', '/certifications/me'),
  addCertification: (data: unknown) => request('POST', '/certifications', data),
};

// ── Employer API ──────────────────────────────────────────────────────────────

export const employerApi = {
  me: () => request('GET', '/employers/me'),
  update: (data: unknown) => request('PUT', '/employers/me', data),
};

// ── Analytics API ─────────────────────────────────────────────────────────────

export const analyticsApi = {
  government: (district?: string) =>
    request('GET', `/analytics/government${district ? `?district=${encodeURIComponent(district)}` : ''}`),
  employment: (district?: string) =>
    request('GET', `/analytics/employment${district ? `?district=${encodeURIComponent(district)}` : ''}`),
  skills: () => request('GET', '/analytics/skills'),
  training: () => request('GET', '/analytics/training'),
};

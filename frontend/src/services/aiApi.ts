import { getToken } from '@/lib/auth';

const BASE = '/api';

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

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

// ── Response shapes ───────────────────────────────────────────────────────────

export interface AIChatData {
  message: string;
  conversation_id: string;
  intent: string;
  is_ai_generated: boolean;
  sources: string[];
  context_used: boolean;
}

export interface AIChatResponse {
  success: boolean;
  data: AIChatData;
}

export interface AIHealthResponse {
  gemini: string;
  groq: string;
  active_llm: string;
  model: string;
  mongodb: string;
  embeddings: string;
  knowledge_base_docs: number;
  fallback_mode: boolean;
}

export interface CareerAdviceData {
  advice: string;
  is_ai_generated: boolean;
  context?: Record<string, unknown>;
}

export interface SkillGapExplainData {
  explanation: string;
  gap_data: Record<string, unknown>;
  is_ai_generated: boolean;
}

export interface DistrictInsightData {
  insight: string;
  district_data: Record<string, unknown>;
  is_ai_generated: boolean;
}

export interface ProgramInsightData {
  insight: string;
  metrics: Record<string, number>;
  is_ai_generated: boolean;
}

export interface TrainingRecommendationData {
  recommendation: string;
  is_ai_generated: boolean;
  programs: unknown[];
}

export interface JobExplanationData {
  explanation: string;
  match_score: number;
  matching_skills: string[];
  missing_skills: string[];
  is_ai_generated: boolean;
}

export interface ConversationListItem {
  id: string;
  intent: string;
  last_message?: { role: string; content: string };
  message_count: number;
  created_at: string;
  updated_at: string;
}

// ── API functions ─────────────────────────────────────────────────────────────

export const aiApi = {
  // Health check — no auth required
  health: () =>
    request<AIHealthResponse>('GET', '/ai/health'),

  // Context-aware chat — returns {success, data: {message, conversation_id, ...}}
  chat: async (message: string, conversation_id?: string): Promise<AIChatData> => {
    const res = await request<AIChatResponse>('POST', '/ai/chat', { message, conversation_id });
    return res.data;
  },

  // Career advice for authenticated trainee
  careerAdvice: async (): Promise<CareerAdviceData> => {
    const res = await request<{ success: boolean; data: CareerAdviceData }>('POST', '/ai/career-advice');
    return res.data;
  },

  // Skill gap explanation
  explainSkillGap: async (target_role?: string): Promise<SkillGapExplainData> => {
    const res = await request<{ success: boolean; data: SkillGapExplainData }>(
      'POST', '/ai/skill-gap-explanation', { target_role }
    );
    return res.data;
  },

  // Job match explanation
  explainJob: async (job_id: string): Promise<JobExplanationData> => {
    const res = await request<{ success: boolean; data: JobExplanationData }>(
      'POST', `/ai/job-explanation?job_id=${encodeURIComponent(job_id)}`
    );
    return res.data;
  },

  // Training recommendation
  trainingRecommendation: async (): Promise<TrainingRecommendationData> => {
    const res = await request<{ success: boolean; data: TrainingRecommendationData }>(
      'POST', '/ai/training-recommendation'
    );
    return res.data;
  },

  // District intelligence insight (govt admin)
  districtInsight: async (district: string): Promise<DistrictInsightData> => {
    const res = await request<{ success: boolean; data: DistrictInsightData }>(
      'POST', '/ai/district-insight', { district }
    );
    return res.data;
  },

  // Program impact insight
  programInsight: async (program_id: string): Promise<ProgramInsightData> => {
    const res = await request<{ success: boolean; data: ProgramInsightData }>(
      'POST', '/ai/program-insight', { program_id }
    );
    return res.data;
  },

  // Conversation management
  conversations: async (): Promise<ConversationListItem[]> => {
    const res = await request<{ success: boolean; data: ConversationListItem[] }>('GET', '/ai/conversations');
    return res.data;
  },

  conversation: async (conv_id: string) => {
    const res = await request<{ success: boolean; data: unknown }>('GET', `/ai/conversations/${conv_id}`);
    return res.data;
  },

  deleteConversation: (conv_id: string) =>
    request<void>('DELETE', `/ai/conversations/${conv_id}`),
};

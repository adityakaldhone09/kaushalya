import { request } from './api';

export interface ChatResponse {
  message: string;
  conversation_id: string;
  is_ai_generated: boolean;
}

export interface CareerAdviceResponse {
  answer: string;
  sources: string[];
  nextSteps: string[];
  isAiGenerated: boolean;
}

export interface SkillGapExplainResponse {
  explanation: string;
  gap_data: any;
  is_ai_generated: boolean;
}

export interface DistrictInsightResponse {
  summary: string;
  district_data: any;
  is_ai_generated: boolean;
}

export interface ProgramInsightResponse {
  explanation: string;
  impact_data: any;
  is_ai_generated: boolean;
}

export const aiApi = {
  chat: (message: string, conversation_id?: string) =>
    request<ChatResponse>('POST', '/ai/chat', { message, conversation_id }),

  careerAdvice: (trainee_id: string, question: string) =>
    request<CareerAdviceResponse>('POST', '/ai/career-advice', { trainee_id, question }),

  explainSkillGap: (target_role: string) =>
    request<SkillGapExplainResponse>('POST', '/ai/explain-skill-gap', { target_role }),

  districtInsight: (district: string) =>
    request<DistrictInsightResponse>('POST', '/ai/district-insight', { district }),

  programInsight: (program_id: string) =>
    request<ProgramInsightResponse>('POST', '/ai/program-insight', { program_id }),

  conversations: () => request<any[]>('GET', '/ai/conversations'),
  
  conversation: (conv_id: string) => request<any>('GET', `/ai/conversations/${conv_id}`),
};

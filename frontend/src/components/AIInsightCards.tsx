import React, { useState, useEffect } from 'react';
import { Sparkles, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { aiApi, CareerAdviceData, DistrictInsightData, ProgramInsightData } from '@/services/aiApi';

// ── Base card ─────────────────────────────────────────────────────────────────

function InsightCard({ title, isAI, children, onRetry }: {
  title: string;
  isAI?: boolean;
  children: React.ReactNode;
  onRetry?: () => void;
}) {
  return (
    <Card className="border-primary/20 bg-primary/5">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center justify-between text-primary text-base">
          <span className="flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            {title}
          </span>
          <div className="flex items-center gap-2">
            {isAI !== undefined && (
              <Badge variant={isAI ? 'default' : 'secondary'} className="text-[10px]">
                {isAI ? 'Gemini AI' : 'Data-driven'}
              </Badge>
            )}
            {onRetry && (
              <button onClick={onRetry} className="text-muted-foreground hover:text-primary transition-colors">
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function LoadingInsight({ title }: { title: string }) {
  return (
    <InsightCard title={title}>
      <div className="flex items-center gap-2 text-muted-foreground py-2">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span className="text-sm">Analysing with KAUSHALYA AI...</span>
      </div>
    </InsightCard>
  );
}

function ErrorInsight({ title, error, onRetry }: { title: string; error: string; onRetry: () => void }) {
  return (
    <InsightCard title={title}>
      <Alert variant="destructive" className="bg-destructive/10 border-destructive/20 text-destructive text-sm">
        <AlertCircle className="w-4 h-4" />
        <AlertTitle className="text-sm">Unavailable</AlertTitle>
        <AlertDescription className="text-xs">{error}</AlertDescription>
      </Alert>
      <Button variant="outline" size="sm" onClick={onRetry} className="mt-3">Retry</Button>
    </InsightCard>
  );
}

// ── Career Recommendation Card ────────────────────────────────────────────────

export function CareerRecommendationCard() {
  const [data, setData] = useState<CareerAdviceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await aiApi.careerAdvice();
      setData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load career advice.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <LoadingInsight title="AI Career Recommendation" />;
  if (error) return <ErrorInsight title="AI Career Recommendation" error={error} onRetry={load} />;
  if (!data) return null;

  return (
    <InsightCard title="AI Career Recommendation" isAI={data.is_ai_generated} onRetry={load}>
      <p className="text-sm leading-relaxed whitespace-pre-line">{data.advice}</p>
    </InsightCard>
  );
}

// ── Skill Gap Explanation Card ────────────────────────────────────────────────

export function SkillGapCard({ targetRole }: { targetRole?: string }) {
  const [data, setData] = useState<{ explanation: string; is_ai_generated: boolean } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await aiApi.explainSkillGap(targetRole);
      setData({ explanation: res.explanation, is_ai_generated: res.is_ai_generated });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to analyse skill gap.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [targetRole]);

  if (loading) return <LoadingInsight title="AI Skill Gap Analysis" />;
  if (error) return <ErrorInsight title="AI Skill Gap Analysis" error={error} onRetry={load} />;
  if (!data) return null;

  return (
    <InsightCard title="AI Skill Gap Analysis" isAI={data.is_ai_generated} onRetry={load}>
      <p className="text-sm leading-relaxed whitespace-pre-line">{data.explanation}</p>
    </InsightCard>
  );
}

// ── District Insight Card ─────────────────────────────────────────────────────

export function DistrictInsightCard({ district }: { district: string }) {
  const [data, setData] = useState<DistrictInsightData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    if (!district) return;
    setLoading(true);
    setError('');
    try {
      const res = await aiApi.districtInsight(district);
      setData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load district insight.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [district]);

  if (!district) return null;
  if (loading) return <LoadingInsight title={`AI Insight: ${district}`} />;
  if (error) return <ErrorInsight title={`AI Insight: ${district}`} error={error} onRetry={load} />;
  if (!data) return null;

  return (
    <InsightCard title={`AI Insight: ${district}`} isAI={data.is_ai_generated} onRetry={load}>
      <p className="text-sm leading-relaxed whitespace-pre-line">{data.insight}</p>
    </InsightCard>
  );
}

// ── Program Insight Card ──────────────────────────────────────────────────────

export function ProgramInsightCard({ programId }: { programId: string }) {
  const [data, setData] = useState<ProgramInsightData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    if (!programId) return;
    setLoading(true);
    setError('');
    try {
      const res = await aiApi.programInsight(programId);
      setData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load program insight.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [programId]);

  if (!programId) return null;
  if (loading) return <LoadingInsight title="AI Program Analysis" />;
  if (error) return <ErrorInsight title="AI Program Analysis" error={error} onRetry={load} />;
  if (!data) return null;

  return (
    <InsightCard title="AI Program Analysis" isAI={data.is_ai_generated} onRetry={load}>
      <p className="text-sm leading-relaxed whitespace-pre-line">{data.insight}</p>
      {data.metrics && Object.keys(data.metrics).length > 0 && (
        <div className="mt-3 grid grid-cols-2 gap-2 pt-3 border-t border-primary/10">
          {Object.entries(data.metrics).map(([k, v]) => (
            <div key={k} className="text-center">
              <div className="font-semibold text-primary text-sm">{typeof v === 'number' ? v : String(v)}</div>
              <div className="text-[10px] text-muted-foreground capitalize">{k.replace(/_/g, ' ')}</div>
            </div>
          ))}
        </div>
      )}
    </InsightCard>
  );
}

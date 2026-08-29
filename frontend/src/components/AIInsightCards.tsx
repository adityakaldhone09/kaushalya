import React, { useState, useEffect } from 'react';
import { Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { aiApi, CareerAdviceResponse, DistrictInsightResponse, ProgramInsightResponse } from '@/services/aiApi';

interface InsightCardProps {
  title: string;
  className?: string;
  children: React.ReactNode;
}

function BaseInsightCard({ title, className = '', children }: InsightCardProps) {
  return (
    <Card className={`border-primary/20 bg-primary/5 ${className}`}>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-primary text-base">
          <Sparkles className="w-5 h-5" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {children}
      </CardContent>
    </Card>
  );
}

export function CareerRecommendationCard({ traineeId, question }: { traineeId: string; question?: string }) {
  const [data, setData] = useState<CareerAdviceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchAdvice = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await aiApi.careerAdvice(traineeId, question || "What should be my next career step?");
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load AI recommendation.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdvice();
  }, [traineeId, question]);

  if (loading) {
    return (
      <BaseInsightCard title="AI Career Recommendation">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Analyzing profile and market demand...</span>
        </div>
      </BaseInsightCard>
    );
  }

  if (error) {
    return (
      <BaseInsightCard title="AI Career Recommendation">
        <Alert variant="destructive" className="bg-destructive/10 border-destructive/20 text-destructive">
          <AlertCircle className="w-4 h-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button variant="outline" size="sm" onClick={fetchAdvice} className="mt-4">Retry</Button>
      </BaseInsightCard>
    );
  }

  if (!data) return null;

  return (
    <BaseInsightCard title="AI Career Recommendation">
      <div className="space-y-4">
        <p className="text-sm leading-relaxed">{data.answer}</p>
        
        {data.nextSteps && data.nextSteps.length > 0 && (
          <div className="mt-4">
            <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">Recommended Next Steps</h4>
            <ul className="space-y-2">
              {data.nextSteps.map((step, idx) => (
                <li key={idx} className="text-sm flex items-start gap-2">
                  <div className="w-5 h-5 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-medium shrink-0 mt-0.5">
                    {idx + 1}
                  </div>
                  <span>{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="pt-2 text-xs text-muted-foreground flex gap-2">
          <span>Sources:</span>
          {data.sources.join(', ')}
        </div>
      </div>
    </BaseInsightCard>
  );
}

export function DistrictInsightCard({ district }: { district: string }) {
  const [data, setData] = useState<DistrictInsightResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchInsight = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await aiApi.districtInsight(district);
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load district insights.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (district) {
      fetchInsight();
    }
  }, [district]);

  if (!district) return null;

  if (loading) {
    return (
      <BaseInsightCard title={`AI Insight: ${district} District`}>
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Analyzing district data...</span>
        </div>
      </BaseInsightCard>
    );
  }

  if (error) {
    return (
      <BaseInsightCard title={`AI Insight: ${district} District`}>
        <Alert variant="destructive" className="bg-destructive/10 border-destructive/20 text-destructive">
          <AlertCircle className="w-4 h-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button variant="outline" size="sm" onClick={fetchInsight} className="mt-4">Retry</Button>
      </BaseInsightCard>
    );
  }

  return (
    <BaseInsightCard title={`AI Insight: ${district} District`}>
      <p className="text-sm leading-relaxed">{data?.summary}</p>
    </BaseInsightCard>
  );
}

export function ProgramInsightCard({ programId }: { programId: string }) {
  const [data, setData] = useState<ProgramInsightResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchInsight = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await aiApi.programInsight(programId);
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load program insights.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (programId) {
      fetchInsight();
    }
  }, [programId]);

  if (!programId) return null;

  if (loading) {
    return (
      <BaseInsightCard title="AI Program Analysis">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Evaluating program impact...</span>
        </div>
      </BaseInsightCard>
    );
  }

  if (error) {
    return (
      <BaseInsightCard title="AI Program Analysis">
        <Alert variant="destructive" className="bg-destructive/10 border-destructive/20 text-destructive">
          <AlertCircle className="w-4 h-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button variant="outline" size="sm" onClick={fetchInsight} className="mt-4">Retry</Button>
      </BaseInsightCard>
    );
  }

  return (
    <BaseInsightCard title="AI Program Analysis">
      <p className="text-sm leading-relaxed">{data?.explanation}</p>
    </BaseInsightCard>
  );
}

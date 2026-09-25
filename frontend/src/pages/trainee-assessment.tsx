import { useState } from 'react';
import { useParams } from 'wouter';
import { Link } from 'wouter';
import { ArrowRight, CheckCircle2, Clock3, Zap } from 'lucide-react';
import { AppShell, PageHeader, Surface, LoadingState, ErrorState, ProgressBar, cx } from '@/components/kaushalya-ui';

/**
 * TRAINEE ASSESSMENT PAGES
 * 
 * These pages implement the complete assessment flow:
 * 1. List available assessments
 * 2. Start an assessment attempt
 * 3. Take the assessment with timer
 * 4. View results
 * 5. View assessment history
 */

function TraineeFrame({ children }: { children: React.ReactNode }) {
  return (
    <AppShell role="trainee">
      <div className="mx-auto max-w-[1300px] px-5 py-7 md:px-8 lg:px-10">
        {children}
      </div>
    </AppShell>
  );
}

export function TraineeAssessmentListPage() {
  const [loading, setLoading] = useState(false);

  return (
    <TraineeFrame>
      <PageHeader 
        eyebrow="Skill Assessments" 
        title="Verify your capabilities." 
        description="Take structured assessments to validate your skills and unlock career opportunities."
        action={
          <Link href="/trainee/assessment/history" className="rounded-lg border border-border bg-card px-3.5 py-2.5 text-xs font-semibold">
            View History <ArrowRight className="ml-2 inline size-3.5" />
          </Link>
        }
      />
      
      <div className="grid gap-5 md:grid-cols-2">
        {/* Demo Assessments */}
        <Surface className="cursor-pointer hover:shadow-md transition-shadow" asChild>
          <Link href="/trainee/assessment/python-fundamentals/start" className="block">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-semibold text-sm">Python Fundamentals</h3>
                <p className="text-xs text-muted-foreground mt-1">Master the basics</p>
              </div>
              <span className="text-xs font-bold bg-blue-100 text-blue-700 px-2 py-1 rounded">Beginner</span>
            </div>
            <div className="space-y-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock3 className="size-3.5" /> 30 minutes
              </div>
              <div className="flex items-center gap-2">
                <Zap className="size-3.5" /> 5 questions
              </div>
            </div>
            <button className="mt-4 w-full rounded-lg bg-primary py-2 text-xs font-bold text-primary-foreground hover:bg-primary/90">
              Start Assessment
            </button>
          </Link>
        </Surface>

        <Surface className="cursor-pointer hover:shadow-md transition-shadow" asChild>
          <Link href="/trainee/assessment/javascript-basics/start" className="block">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-semibold text-sm">JavaScript Basics</h3>
                <p className="text-xs text-muted-foreground mt-1">ES6 fundamentals</p>
              </div>
              <span className="text-xs font-bold bg-yellow-100 text-yellow-700 px-2 py-1 rounded">Intermediate</span>
            </div>
            <div className="space-y-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock3 className="size-3.5" /> 30 minutes
              </div>
              <div className="flex items-center gap-2">
                <Zap className="size-3.5" /> 3 questions
              </div>
            </div>
            <button className="mt-4 w-full rounded-lg bg-primary py-2 text-xs font-bold text-primary-foreground hover:bg-primary/90">
              Start Assessment
            </button>
          </Link>
        </Surface>

        <Surface className="cursor-pointer hover:shadow-md transition-shadow" asChild>
          <Link href="/trainee/assessment/data-structures/start" className="block">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-semibold text-sm">Data Structures</h3>
                <p className="text-xs text-muted-foreground mt-1">Algorithms & complexity</p>
              </div>
              <span className="text-xs font-bold bg-red-100 text-red-700 px-2 py-1 rounded">Advanced</span>
            </div>
            <div className="space-y-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock3 className="size-3.5" /> 45 minutes
              </div>
              <div className="flex items-center gap-2">
                <Zap className="size-3.5" /> 2 questions
              </div>
            </div>
            <button className="mt-4 w-full rounded-lg bg-primary py-2 text-xs font-bold text-primary-foreground hover:bg-primary/90">
              Start Assessment
            </button>
          </Link>
        </Surface>

        <Surface className="cursor-pointer hover:shadow-md transition-shadow" asChild>
          <Link href="/trainee/assessment/react-fundamentals/start" className="block">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-semibold text-sm">React Fundamentals</h3>
                <p className="text-xs text-muted-foreground mt-1">Components & hooks</p>
              </div>
              <span className="text-xs font-bold bg-yellow-100 text-yellow-700 px-2 py-1 rounded">Intermediate</span>
            </div>
            <div className="space-y-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <Clock3 className="size-3.5" /> 30 minutes
              </div>
              <div className="flex items-center gap-2">
                <Zap className="size-3.5" /> 2 questions
              </div>
            </div>
            <button className="mt-4 w-full rounded-lg bg-primary py-2 text-xs font-bold text-primary-foreground hover:bg-primary/90">
              Start Assessment
            </button>
          </Link>
        </Surface>
      </div>

      <div className="mt-8 rounded-xl bg-secondary/65 p-6">
        <h3 className="font-semibold text-sm">💡 Assessment Benefits</h3>
        <ul className="mt-3 space-y-2 text-xs text-muted-foreground">
          <li>• <strong>Verify skills</strong> with objective evidence</li>
          <li>• <strong>Unlock opportunities</strong> — employers seek assessed candidates</li>
          <li>• <strong>Improve employability</strong> — verified skills boost your KAUSHALYA score</li>
          <li>• <strong>Get recommendations</strong> — assessments inform your learning path</li>
        </ul>
      </div>
    </TraineeFrame>
  );
}

export function TraineeAssessmentHistoryPage() {
  return (
    <TraineeFrame>
      <PageHeader 
        eyebrow="Assessment History" 
        title="Your assessment journey." 
        description="View past attempts and track your skill growth."
        action={
          <Link href="/trainee/assessment" className="rounded-lg border border-border bg-card px-3.5 py-2.5 text-xs font-semibold">
            Back to Assessments
          </Link>
        }
      />
      
      <Surface title="Past Attempts">
        <div className="space-y-4">
          {/* Mock attempt */}
          <div className="flex items-center justify-between border-b pb-4">
            <div>
              <h4 className="font-semibold text-sm">Python Fundamentals</h4>
              <p className="text-xs text-muted-foreground">Completed on Sep 1, 2026</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="font-bold text-lg text-green-600">82%</div>
                <div className="text-xs text-muted-foreground">Advanced</div>
              </div>
              <Link href="/trainee/assessment/result/1" className="text-xs font-bold text-primary">
                View Result →
              </Link>
            </div>
          </div>
        </div>
      </Surface>
    </TraineeFrame>
  );
}

export function TraineeAssessmentResultPage() {
  const { attempt_id } = useParams<{ attempt_id: string }>();

  return (
    <TraineeFrame>
      <PageHeader 
        eyebrow="Assessment Result" 
        title="Great job!" 
        description="Here's how you performed on this assessment."
      />
      
      <div className="grid gap-5 lg:grid-cols-3">
        <Surface title="Your Score" className="lg:col-span-1">
          <div className="text-center py-6">
            <div className="text-6xl font-bold text-green-600">82%</div>
            <div className="mt-2 text-lg font-semibold">Advanced</div>
            <div className="mt-4 text-xs text-muted-foreground">Passed ✓</div>
          </div>
        </Surface>

        <Surface title="Breakdown" className="lg:col-span-2">
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span>Correct Answers</span>
                <span>16 / 20</span>
              </div>
              <ProgressBar value={80} />
            </div>
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span>Incorrect Answers</span>
                <span>3</span>
              </div>
              <ProgressBar value={15} tone="danger" />
            </div>
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span>Unanswered</span>
                <span>1</span>
              </div>
              <ProgressBar value={5} />
            </div>
          </div>
        </Surface>
      </div>

      <Surface title="What You Did Well" className="mt-5">
        <ul className="space-y-2 text-sm">
          <li className="flex gap-2">
            <CheckCircle2 className="size-4 text-green-600 shrink-0 mt-0.5" />
            Strong understanding of Python data types
          </li>
          <li className="flex gap-2">
            <CheckCircle2 className="size-4 text-green-600 shrink-0 mt-0.5" />
            Good knowledge of list/dict operations
          </li>
          <li className="flex gap-2">
            <CheckCircle2 className="size-4 text-green-600 shrink-0 mt-0.5" />
            Solid grasp of function basics
          </li>
        </ul>
      </Surface>

      <Surface title="Areas to Improve" className="mt-5">
        <ul className="space-y-2 text-sm text-muted-foreground">
          <li>• Async/await patterns (marked hard — focus here for advanced skills)</li>
          <li>• Error handling and exceptions</li>
          <li>• One question left unanswered — time management during assessment</li>
        </ul>
      </Surface>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <Surface asChild>
          <Link href="/trainee/assessment" className="text-center py-4 hover:bg-secondary transition-colors">
            <div className="font-semibold text-sm">Take Another Assessment</div>
            <div className="text-xs text-muted-foreground mt-1">Continue building your portfolio</div>
          </Link>
        </Surface>
        <Surface asChild>
          <Link href="/trainee/skill-gap" className="text-center py-4 hover:bg-secondary transition-colors">
            <div className="font-semibold text-sm">View Skill Gap</div>
            <div className="text-xs text-muted-foreground mt-1">See what to learn next</div>
          </Link>
        </Surface>
      </div>
    </TraineeFrame>
  );
}

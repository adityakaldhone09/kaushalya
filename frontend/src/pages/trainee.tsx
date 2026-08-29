import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { ArrowRight, BadgeCheck, BookOpen, CheckCircle2, ChevronRight, Clock3, Lightbulb, MapPin, Pencil, Send, Sparkles, Target } from 'lucide-react';
import { Link } from 'wouter';
import { getGetJobMatchesQueryKey, getGetTraineeQueryKey, useApplyToJob, useGetCareerAdvice, useGetJobMatches, useGetTrainee, useGetTraineeDashboard, useGetTraineeRecommendations, useListSkills, useListTrainingPrograms, useUpdateTrainee } from '@workspace/api-client-react';
import { AppShell, EmptyState, ErrorState, KpiCard, LoadingState, PageHeader, ProgressBar, Surface, cx } from '@/components/kaushalya-ui';
import { useAuth } from '@/contexts/AuthContext';

function useTraineeId(): string {
  const { user } = useAuth();
  // Use authenticated user ID if available, fall back to demo seed ID
  return user?.id || 'trainee@kaushalya.demo';
}

function TraineeFrame({ children }: { children: React.ReactNode }) { return <AppShell role="trainee"><div className="mx-auto max-w-[1300px] px-5 py-7 md:px-8 lg:px-10">{children}</div></AppShell>; }
function useTraineeData() {
  const traineeId = useTraineeId();
  return useGetTraineeDashboard(traineeId);
}

export function TraineeDashboardPage() {
  const query = useTraineeData();
  const data = query.data;
  if (query.isLoading) return <TraineeFrame><PageHeader eyebrow="My workspace" title="Your next move starts here." /><LoadingState label="Loading your journey" /></TraineeFrame>;
  if (query.isError || !data) return <TraineeFrame><PageHeader eyebrow="My workspace" title="Your next move starts here." /><ErrorState onRetry={() => query.refetch()} /></TraineeFrame>;
  const trainee = data.trainee;
  return <TraineeFrame>
    <PageHeader eyebrow={`Good morning, ${trainee.name.split(' ')[0]}`} title="Your next move starts here." description="A focused view of your progress, the skills to build next, and opportunities aligned to your profile." action={<Link href="/trainee/profile" data-testid="link-dashboard-profile" className="rounded-lg border border-border bg-card px-3.5 py-2.5 text-xs font-semibold"><Pencil className="mr-2 inline size-3.5" />Update profile</Link>} />
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard label="Employability score" value={`${trainee.employabilityScore}`} change={trainee.scoreClass} detail="Based on verified skills and readiness" index={0} />
      <KpiCard label="Skills in profile" value={`${data.totalSkills}`} change={`${data.verifiedSkills} verified`} detail="Keep your evidence current" index={1} />
      <KpiCard label="Skill gap score" value={`${data.skillGapScore}`} detail="Lower is closer to your target" trend="down" index={2} />
      <KpiCard label="Job matches" value={`${data.recommendedJobs}`} detail="Ranked to your profile" index={3} />
    </div>
    <div className="mt-5 grid gap-5 lg:grid-cols-[1.1fr_.9fr]">
      <Surface title="Your journey" meta="Profile to placement">
        <div className="space-y-1">{data.journey.map((step, i) => <div key={step.label} className="flex gap-4 py-3" data-testid={`row-journey-${i}`}>
          <div className={cx("relative grid size-8 shrink-0 place-items-center rounded-full border", step.status === 'complete' ? "border-primary bg-primary text-primary-foreground" : step.status === 'current' ? "border-accent bg-accent text-accent-foreground" : "border-border bg-muted text-muted-foreground")}>{step.status === 'complete' ? <CheckCircle2 className="size-4" /> : <span className="font-mono text-xs">{i + 1}</span>}{i < data.journey.length - 1 && <span className="absolute left-1/2 top-8 h-8 w-px bg-border" />}</div>
          <div className="flex-1"><div className="flex items-center justify-between gap-3"><h3 className="text-sm font-semibold">{step.label}</h3>{step.date && <span className="text-[10px] text-muted-foreground">{step.date}</span>}</div><p className="mt-1 text-xs text-muted-foreground">{step.detail}</p></div>
        </div>)}</div>
      </Surface>
      <Surface title="Recent activity" meta="Latest signals">
        <div className="space-y-4">{data.recentActivity.map((activity, i) => <div key={`${activity.title}-${i}`} className="flex gap-3" data-testid={`row-activity-${i}`}>
          <div className={cx("mt-0.5 grid size-7 shrink-0 place-items-center rounded-lg", activity.tone === 'green' ? "bg-[#e3f1e4] text-[#317954]" : activity.tone === 'amber' ? "bg-[#f8eccb] text-[#896d25]" : "bg-secondary text-primary")}><Clock3 className="size-3.5" /></div>
          <div className="min-w-0 flex-1"><div className="text-xs font-semibold">{activity.title}</div><p className="mt-1 text-[11px] leading-4 text-muted-foreground">{activity.detail}</p></div><span className="text-[10px] text-muted-foreground">{activity.time}</span>
        </div>)}{!data.recentActivity.length && <EmptyState title="Your activity will show here" detail="Complete a profile step or apply to a role to start your timeline." />}</div>
      </Surface>
    </div>
    <div className="mt-5 grid gap-5 lg:grid-cols-[.8fr_1.2fr]">
      <Surface title="Skills to strengthen" meta={`${data.skillGapScore} gap score`}>
        <div className="space-y-4">{trainee.skills.slice(0, 4).map((skill) => <div key={skill.skill}><div className="mb-1.5 flex justify-between text-xs"><span className="font-semibold">{skill.skill}</span><span className="text-muted-foreground">{skill.proficiency}%</span></div><ProgressBar value={skill.proficiency} tone={skill.proficiency < 55 ? 'danger' : 'primary'} /></div>)}</div>
        <Link href="/trainee/skill-gap" data-testid="link-dashboard-skill-gap" className="mt-5 inline-flex items-center text-xs font-bold text-primary">View your skill gap <ArrowRight className="ml-1 size-3.5" /></Link>
      </Surface>
      <Surface title="Recommended career paths" meta="Based on your profile">
        <div className="flex flex-wrap gap-2">{data.careerPaths.map((path) => <span key={path} className="rounded-full border border-border bg-muted/60 px-3 py-2 text-xs font-semibold">{path}</span>)}</div>
        <div className="mt-6 rounded-xl bg-secondary/65 p-4"><div className="flex items-start gap-3"><Sparkles className="mt-0.5 size-4 text-primary" /><div><div className="text-xs font-semibold">A small action compounds</div><p className="mt-1 text-[11px] leading-5 text-muted-foreground">One verified skill can unlock more relevant roles and improve the confidence of your matches.</p></div></div></div>
      </Surface>
    </div>
  </TraineeFrame>;
}

export function TraineeProfilePage() {
  const traineeId = useTraineeId();
  const profile = useGetTrainee(traineeId);
  const queryClient = useQueryClient();
  const update = useUpdateTrainee();
  const trainee = profile.data;
  function submit(e: React.FormEvent<HTMLFormElement>) { e.preventDefault(); const f = new FormData(e.currentTarget); update.mutate({ traineeId, data: { name: String(f.get('name')), phone: String(f.get('phone')), district: String(f.get('district')), education: String(f.get('education')), specialization: String(f.get('specialization')), targetCareer: String(f.get('targetCareer')) } }, { onSuccess: () => queryClient.invalidateQueries({ queryKey: getGetTraineeQueryKey(traineeId) }) }); }
  return <TraineeFrame><PageHeader eyebrow="Your profile" title="Make your signal count." description="Keep the details that shape your matches accurate and current." />{profile.isLoading ? <LoadingState /> : profile.isError || !trainee ? <ErrorState onRetry={() => profile.refetch()} /> : <form onSubmit={submit} className="max-w-3xl space-y-5" data-testid="form-trainee-profile"><Surface title="Personal details"><div className="grid gap-4 sm:grid-cols-2"><Field name="name" label="Full name" value={trainee.name} /><Field name="phone" label="Phone" value={trainee.phone} /><Field name="district" label="District" value={trainee.district} /><Field name="education" label="Education" value={trainee.education} /><Field name="specialization" label="Specialization" value={trainee.specialization} /><Field name="targetCareer" label="Target career" value={trainee.specialization} /></div></Surface><Surface title="Current position" meta="Read-only from your outcome record"><div className="grid gap-4 sm:grid-cols-3"><Stat label="Status" value={trainee.employmentStatus} /><Stat label="Experience" value={trainee.experience} /><Stat label="State" value={trainee.state} /></div></Surface><div className="flex items-center gap-3"><button disabled={update.isPending} data-testid="button-save-profile" className="rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground disabled:opacity-60">{update.isPending ? 'Saving…' : 'Save profile'}</button>{update.isSuccess && <span className="text-xs font-semibold text-[#317954]" data-testid="status-profile-saved">Profile updated</span>}</div></form>}</TraineeFrame>;
}
function Field({ name, label, value }: { name: string; label: string; value: string }) { return <label className="block text-xs font-semibold">{label}<input required name={name} defaultValue={value} data-testid={`input-trainee-${name}`} className="mt-2 h-10 w-full rounded-lg border border-border bg-background px-3 text-sm font-normal outline-none focus:ring-2 focus:ring-ring" /></label>; }
function Stat({ label, value }: { label: string; value: string }) { return <div><div className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</div><div className="mt-1 text-sm font-semibold capitalize">{value}</div></div>; }

export function TraineeSkillsPage() {
  const traineeId = useTraineeId();
  const query = useGetTrainee(traineeId);
  const taxonomy = useListSkills();
  const skills = query.data?.skills ?? [];
  return <TraineeFrame><PageHeader eyebrow="Your skills" title="Show what you can do." description="Verified capability is the strongest signal in your profile. Keep it clear, current and evidence-backed." action={<Link href="/trainee/skill-gap" data-testid="link-skills-gap" className="rounded-lg bg-primary px-3.5 py-2.5 text-xs font-bold text-primary-foreground">See skill gap <ArrowRight className="ml-1 inline size-3.5" /></Link>} />{query.isLoading ? <LoadingState /> : query.isError ? <ErrorState onRetry={() => query.refetch()} /> : <div className="grid gap-3 md:grid-cols-2"><div className="md:col-span-2 flex items-center gap-2 text-xs text-muted-foreground"><span className="size-2 rounded-full bg-primary" />{taxonomy.data?.length ?? 0} skills in the shared taxonomy</div>{skills.map((skill) => <div key={skill.skill} className="rounded-2xl border border-card-border bg-card p-5 shadow-[var(--shadow-soft)]" data-testid={`card-trainee-skill-${skill.skill}`}><div className="flex items-start justify-between"><div><div className="text-[10px] uppercase tracking-wider text-muted-foreground">{skill.category}</div><h2 className="mt-1 font-display text-lg font-semibold">{skill.skill}</h2></div>{skill.verified && <span className="flex items-center gap-1 rounded-full bg-[#e3f1e4] px-2 py-1 text-[10px] font-semibold text-[#317954]"><BadgeCheck className="size-3" />Verified</span>}</div><div className="mt-6 flex items-end justify-between"><div><div className="font-display text-3xl font-semibold">{skill.proficiency}%</div><div className="text-[10px] text-muted-foreground">proficiency · {skill.level}</div></div><div className="text-right"><div className="text-sm font-semibold">{skill.assessmentScore}</div><div className="text-[10px] text-muted-foreground">assessment score</div></div></div><div className="mt-3"><ProgressBar value={skill.proficiency} /></div></div>)}{!skills.length && <EmptyState title="Add your first skill" detail="Skills will appear here after your profile or assessment is connected." />}</div>}</TraineeFrame>;
}

export function TraineeGapPage() {
  const traineeId = useTraineeId();
  const query = useGetTrainee(traineeId);
  const skills = query.data?.skills ?? [];
  return <TraineeFrame><PageHeader eyebrow="Skill gap" title="Know what to build next." description="Your gap is a practical to-do list—not a verdict. Prioritise the skills that move your target career closer." />{query.isLoading ? <LoadingState /> : query.isError ? <ErrorState onRetry={() => query.refetch()} /> : <div className="grid gap-5 lg:grid-cols-[1.1fr_.9fr]"><Surface title="Capability map" meta="Current profile"><div className="space-y-5">{skills.map((skill) => <div key={skill.skill}><div className="mb-2 flex items-center justify-between"><div><span className="text-sm font-semibold">{skill.skill}</span><span className="ml-2 text-[10px] text-muted-foreground">{skill.category}</span></div><span className={cx("text-xs font-bold", skill.proficiency < 55 ? "text-[#b34e41]" : "text-primary")}>{skill.proficiency < 55 ? 'Priority' : 'Building'}</span></div><ProgressBar value={skill.proficiency} tone={skill.proficiency < 55 ? 'danger' : 'primary'} /></div>)}</div></Surface><Surface title="How to close the gap"><div className="space-y-4"><AdviceStep icon={Target} title="Choose one priority" text="Start with the skill that appears in the most relevant opportunities." /><AdviceStep icon={BookOpen} title="Practice in a real context" text="A completed project is easier to verify than a list of intentions." /><AdviceStep icon={BadgeCheck} title="Get it verified" text="Assessment evidence helps your profile travel further." /></div><Link href="/trainee/training" data-testid="link-gap-training" className="mt-6 inline-flex items-center text-xs font-bold text-primary">Find a training option <ArrowRight className="ml-1 size-3.5" /></Link></Surface></div>}</TraineeFrame>;
}
function AdviceStep({ icon: Icon, title, text }: { icon: typeof Target; title: string; text: string }) { return <div className="flex gap-3"><div className="grid size-8 shrink-0 place-items-center rounded-lg bg-secondary text-primary"><Icon className="size-4" /></div><div><div className="text-xs font-semibold">{title}</div><p className="mt-1 text-[11px] leading-5 text-muted-foreground">{text}</p></div></div>; }

export function TraineeJobsPage() {
  const traineeId = useTraineeId();
  const matches = useGetJobMatches(traineeId);
  const queryClient = useQueryClient();
  const apply = useApplyToJob();
  const [applied, setApplied] = useState<string[]>([]);
  const jobs = matches.data ?? [];
  return <TraineeFrame><PageHeader eyebrow="Job matches" title="Opportunities that fit." description="Ranked by the skills you already have and the capability you can build next." action={<Link href="/trainee/profile" data-testid="link-jobs-update-profile" className="rounded-lg border border-border bg-card px-3.5 py-2.5 text-xs font-semibold">Tune my profile</Link>} />{matches.isLoading ? <LoadingState /> : matches.isError ? <ErrorState onRetry={() => matches.refetch()} /> : <div className="space-y-3">{jobs.map((job) => <div key={job.id} className="rounded-2xl border border-card-border bg-card p-5 shadow-[var(--shadow-soft)]" data-testid={`card-job-match-${job.id}`}><div className="flex flex-col justify-between gap-4 sm:flex-row"><div><div className="flex flex-wrap items-center gap-2"><span className="rounded-full bg-accent/35 px-2 py-1 text-[10px] font-bold text-[#806822]">{job.match}% match</span><span className="text-[11px] text-muted-foreground">{job.jobType}</span></div><h2 className="mt-3 font-display text-xl font-semibold">{job.title}</h2><div className="mt-1 flex flex-wrap gap-3 text-xs text-muted-foreground"><span>{job.company}</span><span><MapPin className="mr-1 inline size-3" />{job.location}</span><span>{job.salary}</span></div></div><div className="flex items-start sm:items-center"><button disabled={applied.includes(job.id) || apply.isPending} onClick={() => apply.mutate({ jobId: job.id, data: { traineeId: traineeId, note: 'Application submitted from KAUSHALYA.' } }, { onSuccess: () => { setApplied((old) => [...old, job.id]); queryClient.invalidateQueries({ queryKey: getGetJobMatchesQueryKey(traineeId) }); } })} data-testid={`button-apply-job-${job.id}`} className={cx("rounded-lg px-4 py-2.5 text-xs font-bold", applied.includes(job.id) ? "bg-[#e3f1e4] text-[#317954]" : "bg-primary text-primary-foreground")}>{applied.includes(job.id) ? <><CheckCircle2 className="mr-1 inline size-3.5" />Applied</> : 'Apply now'}</button></div></div><div className="mt-5 grid gap-3 border-t border-border pt-4 sm:grid-cols-2"><div><div className="text-[10px] uppercase tracking-wider text-muted-foreground">Why it matches</div><p className="mt-1 text-xs leading-5">{job.matchReason}</p></div><div><div className="text-[10px] uppercase tracking-wider text-muted-foreground">Your signal</div><div className="mt-2 flex flex-wrap gap-1.5">{job.matchingSkills.slice(0, 4).map((skill) => <span key={skill} className="rounded-md bg-secondary px-2 py-1 text-[10px] font-semibold text-primary">{skill}</span>)}</div></div></div></div>)}{!jobs.length && <EmptyState title="No matches yet" detail="Complete your profile and verify more skills to improve your match signal." />}</div>}</TraineeFrame>;
}

export function TraineeTrainingPage() {
  const query = useListTrainingPrograms();
  const programs = query.data ?? [];
  return <TraineeFrame><PageHeader eyebrow="Training" title="Choose your next capability." description="Practical programs connected to the skills employers are asking for." />{query.isLoading ? <LoadingState /> : query.isError ? <ErrorState onRetry={() => query.refetch()} /> : <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{programs.map((program) => <div key={program.id} className="rounded-2xl border border-card-border bg-card p-5 shadow-[var(--shadow-soft)]"><div className="flex items-center justify-between"><span className="rounded-full bg-secondary px-2 py-1 text-[10px] font-bold text-primary">{program.mode}</span><span className="text-[10px] text-muted-foreground">{program.duration}</span></div><h2 className="mt-5 font-display text-xl font-semibold">{program.name}</h2><p className="mt-2 text-xs leading-5 text-muted-foreground">{program.description}</p><div className="mt-5 flex flex-wrap gap-1.5">{program.skills.slice(0, 3).map((skill) => <span key={skill} className="rounded-md border border-border px-2 py-1 text-[10px]">{skill}</span>)}</div><div className="mt-5 border-t border-border pt-4 text-xs"><div className="flex justify-between"><span className="text-muted-foreground">Placement rate</span><span className="font-semibold">{program.placementRate}%</span></div><ProgressBar value={program.placementRate} /><button data-testid={`button-view-training-${program.id}`} className="mt-4 text-xs font-bold text-primary">View program <ArrowRight className="ml-1 inline size-3.5" /></button></div></div>)}{!programs.length && <EmptyState title="No training programs available" detail="New options will appear as institutes publish programs." />}</div>}</TraineeFrame>;
}

export function TraineeRecommendationsPage() {
  const traineeId = useTraineeId();
  const query = useGetTraineeRecommendations(traineeId);
  const advice = useGetCareerAdvice();
  const [question, setQuestion] = useState('');
  const recs = query.data ?? [];
  function ask(e: React.FormEvent) { e.preventDefault(); if (!question.trim()) return; advice.mutate({ data: { traineeId: traineeId, question } }); }
  return <TraineeFrame><PageHeader eyebrow="Recommendations" title="Guidance with a reason." description="Personalised suggestions connected to your skills, target career and the market around you." />{query.isLoading ? <LoadingState /> : query.isError ? <ErrorState onRetry={() => query.refetch()} /> : <div className="grid gap-5 lg:grid-cols-[1fr_.85fr]"><Surface title="Your next best moves" meta={`${recs.length} recommendations`}><div className="space-y-3">{recs.map((rec) => <div key={rec.id} className="rounded-xl border border-border p-4"><div className="flex items-start justify-between gap-3"><div><div className="flex items-center gap-2"><span className={cx("rounded-full px-2 py-1 text-[10px] font-bold capitalize", rec.priority === 'high' ? "bg-[#f5d4ca] text-[#974234]" : "bg-[#f8eccb] text-[#896d25]")}>{rec.priority} priority</span><span className="text-[10px] uppercase tracking-wider text-muted-foreground">{rec.type}</span></div><h3 className="mt-3 text-sm font-semibold">{rec.title}</h3><p className="mt-1 text-xs leading-5 text-muted-foreground">{rec.description}</p></div><ChevronRight className="size-4 shrink-0 text-primary" /></div><div className="mt-3 text-xs font-bold text-primary">{rec.action} <ArrowRight className="ml-1 inline size-3.5" /></div></div>)}{!recs.length && <EmptyState title="No recommendations yet" detail="Your next best moves will appear as your profile becomes richer." />}</div></Surface><Surface title="Ask the career guide" meta="KAUSHALYA AI"><div className="rounded-xl bg-secondary/60 p-4"><div className="flex gap-3"><Lightbulb className="mt-0.5 size-4 text-primary" /><p className="text-xs leading-5 text-muted-foreground">Ask a practical question about your next skill, training choice or job search.</p></div></div><form onSubmit={ask} className="mt-4" data-testid="form-career-advice"><textarea value={question} onChange={(e) => setQuestion(e.target.value)} required rows={4} placeholder="What should I focus on next?" data-testid="input-career-question" className="w-full resize-none rounded-xl border border-border bg-background p-3 text-sm outline-none focus:ring-2 focus:ring-ring" /><button disabled={advice.isPending} data-testid="button-ask-career-advice" className="mt-3 rounded-lg bg-primary px-4 py-2.5 text-xs font-bold text-primary-foreground disabled:opacity-60"><Send className="mr-1.5 inline size-3.5" />{advice.isPending ? 'Thinking…' : 'Ask guide'}</button></form>{advice.data && <div className="mt-5 rounded-xl border border-primary/25 bg-[#e9eee8] p-4" data-testid="card-career-advice"><div className="text-xs font-semibold">{advice.data.answer}</div><div className="mt-4 text-[10px] font-bold uppercase tracking-wider text-primary">Next steps</div><ul className="mt-2 space-y-2">{advice.data.nextSteps.map((step) => <li key={step} className="flex gap-2 text-xs text-muted-foreground"><CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-primary" />{step}</li>)}</ul></div>}</Surface></div>}</TraineeFrame>;
}
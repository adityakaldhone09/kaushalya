import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { ArrowRight, BriefcaseBusiness, Building2, Eye, EyeOff, Landmark, Network, ShieldCheck, UserRound } from 'lucide-react';
import { Link, useLocation } from 'wouter';
import { getListJobsQueryKey, useCreateJob, useListJobs, useListTrainingPrograms } from '@workspace/api-client-react';
import { AppShell, EmptyState, ErrorState, LoadingState, PageHeader, ProgressBar, Surface, cx } from '@/components/kaushalya-ui';
import { useAuth } from '@/contexts/AuthContext';
import { authApi } from '@/services/api';
import { roleDashboard } from '@/lib/auth';

const ROLE_API_MAP: Record<string, string> = {
  government: 'GOVERNMENT_ADMIN',
  trainee: 'TRAINEE',
  employer: 'EMPLOYER',
  institute: 'TRAINING_INSTITUTE',
};

export function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const [, setLocation] = useLocation();
  const { login } = useAuth();
  const [role, setRole] = useState<'government' | 'trainee' | 'employer' | 'institute'>('trainee');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const isLogin = mode === 'login';

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError('');
    setLoading(true);
    const form = new FormData(e.currentTarget);
    const email = String(form.get('email') || '');
    const password = String(form.get('password') || '');
    const name = String(form.get('name') || '');

    try {
      let res;
      if (isLogin) {
        res = await authApi.login({ email, password });
      } else {
        res = await authApi.register({
          name,
          email,
          password,
          role: ROLE_API_MAP[role] || 'TRAINEE',
        });
      }
      login(res.access_token, {
        id: res.user.id,
        name: res.user.name,
        email: res.user.email,
        role: res.user.role,
        organization: res.user.organization,
      });
      setLocation(roleDashboard(res.user.role));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  }

  return <div className="noise grid min-h-[100dvh] bg-[#e9eee8] lg:grid-cols-[.9fr_1.1fr]"><div className="relative hidden overflow-hidden bg-[#203f43] p-10 text-[#edf0e6] lg:flex lg:flex-col lg:justify-between"><Link href="/" data-testid="link-auth-logo"><div><div className="flex items-center gap-3"><div className="grid size-9 place-items-center rounded-xl bg-accent text-accent-foreground"><span className="font-display text-lg font-bold">K</span></div><span className="font-display text-[15px] font-bold tracking-[.14em]">KAUSHALYA</span></div><div className="mt-20 max-w-md"><div className="text-[10px] font-bold uppercase tracking-[.2em] text-accent">One system, many futures</div><h1 className="mt-5 font-display text-6xl font-semibold leading-[.93] tracking-[-.07em]">The next step is clearer when the signal is shared.</h1><p className="mt-7 text-sm leading-6 text-[#afc5bc]">Enter a workspace designed around your role—and connected to the workforce story beyond it.</p></div></div><div className="flex items-center justify-between text-xs text-[#afc5bc]"><span>Public workforce intelligence</span><span>KAUSHALYA / 01</span></div></Link></div><div className="flex items-center justify-center p-5 sm:p-10"><div className="w-full max-w-[460px]"><div className="mb-8 lg:hidden"><Link href="/" data-testid="mobile-auth-logo" className="inline-block"><div className="flex items-center gap-3"><div className="grid size-9 place-items-center rounded-xl bg-accent text-accent-foreground"><span className="font-display text-lg font-bold">K</span></div><span className="font-display text-[15px] font-bold tracking-[.14em]">KAUSHALYA</span></div></Link></div><div className="mb-8"><div className="text-[10px] font-bold uppercase tracking-[.2em] text-primary">{isLogin ? 'Welcome back' : 'Create your workspace'}</div><h2 className="mt-3 font-display text-4xl font-semibold tracking-[-.06em]">{isLogin ? 'Continue the work.' : 'Start with your role.'}</h2><p className="mt-3 text-sm text-muted-foreground">{isLogin ? 'Sign in with your demo account.' : 'A focused entry point for every part of the workforce system.'}</p></div>{!isLogin && <div className="mb-6 grid grid-cols-2 gap-2 sm:grid-cols-4">{([['government', Landmark, 'Government'], ['trainee', UserRound, 'Trainee'], ['employer', BriefcaseBusiness, 'Employer'], ['institute', Building2, 'Institute']] as const).map(([value, Icon, label]) => <button key={value} type="button" onClick={() => setRole(value)} data-testid={`button-role-${value}`} className={cx("rounded-xl border p-3 text-center transition-colors", role === value ? "border-primary bg-secondary text-primary" : "border-border bg-card text-muted-foreground hover:bg-muted")}><Icon className="mx-auto mb-2 size-4" /><span className="text-[10px] font-semibold">{label}</span></button>)}</div>}<form onSubmit={submit} className="space-y-4" data-testid={`form-${mode}`}>{!isLogin && <label className="block text-xs font-semibold">Full name<input required name="name" placeholder="Your full name" data-testid="input-auth-name" className="mt-2 h-11 w-full rounded-xl border border-border bg-card px-3.5 text-sm font-normal outline-none focus:ring-2 focus:ring-ring" /></label>}<label className="block text-xs font-semibold">Work email<input required name="email" type="email" placeholder="you@organisation.gov" data-testid="input-auth-email" className="mt-2 h-11 w-full rounded-xl border border-border bg-card px-3.5 text-sm font-normal outline-none focus:ring-2 focus:ring-ring" /></label><label className="block text-xs font-semibold">Password<div className="relative mt-2"><input required name="password" type={showPassword ? 'text' : 'password'} placeholder="At least 8 characters" data-testid="input-auth-password" className="h-11 w-full rounded-xl border border-border bg-card px-3.5 pr-11 text-sm font-normal outline-none focus:ring-2 focus:ring-ring" /><button type="button" onClick={() => setShowPassword(!showPassword)} data-testid="button-toggle-password" className="absolute right-3 top-3 text-muted-foreground">{showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}</button></div></label>{error && <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive" data-testid="error-auth">{error}</div>}<button disabled={loading} data-testid={`button-submit-${mode}`} className="w-full rounded-xl bg-primary py-3 text-sm font-bold text-primary-foreground shadow-lg shadow-primary/10 hover:bg-primary/90 disabled:opacity-60">{loading ? 'Please wait…' : isLogin ? 'Enter workspace' : 'Create workspace'} {!loading && <ArrowRight className="ml-1.5 inline size-4" />}</button></form><div className="mt-6 flex items-start gap-2 rounded-xl border border-border bg-card/60 p-3 text-[11px] leading-4 text-muted-foreground"><ShieldCheck className="mt-0.5 size-4 shrink-0 text-primary" /><span>Demo accounts: <code className="text-primary">trainee@kaushalya.demo</code> / <code className="text-primary">admin@kaushalya.demo</code> · Password: <code className="text-primary">Demo@1234</code></span></div><p className="mt-6 text-center text-xs text-muted-foreground">{isLogin ? "New to KAUSHALYA?" : 'Already have access?'} <Link href={isLogin ? '/register' : '/login'} data-testid="link-auth-switch" className="font-bold text-primary">{isLogin ? 'Create a workspace' : 'Sign in'}</Link></p></div></div></div>;
}

function EmployerFrame({ children }: { children: React.ReactNode }) { return <AppShell role="employer"><div className="mx-auto max-w-[1300px] px-5 py-7 md:px-8 lg:px-10">{children}</div></AppShell>; }
function InstituteFrame({ children }: { children: React.ReactNode }) { return <AppShell role="institute"><div className="mx-auto max-w-[1300px] px-5 py-7 md:px-8 lg:px-10">{children}</div></AppShell>; }

export function EmployerDashboardPage() {
  const jobs = useListJobs();
  const rows = jobs.data ?? [];
  return <EmployerFrame><PageHeader eyebrow="Employer workspace" title="Build the team you need." description="Keep open roles, applicant signal and local capability in one view." action={<Link href="/employer/jobs" data-testid="link-employer-jobs" className="rounded-lg bg-primary px-3.5 py-2.5 text-xs font-bold text-primary-foreground">Manage jobs <ArrowRight className="ml-1 inline size-3.5" /></Link>} /><div className="grid gap-4 sm:grid-cols-3"><Metric label="Open roles" value={`${rows.length}`} detail="Connected to the talent pool" /><Metric label="Applicants" value={`${rows.reduce((sum, row) => sum + row.applicants, 0)}`} detail="Across open roles" /><Metric label="Top match" value={`${Math.max(...rows.map((row) => row.match), 0)}%`} detail="Current candidate signal" /></div><div className="mt-5 grid gap-5 lg:grid-cols-[1.1fr_.9fr]"><Surface title="Open roles" meta="Recent postings"><RoleList rows={rows.slice(0, 5)} /></Surface><Surface title="A stronger signal" meta="Employer note"><div className="rounded-xl bg-secondary/70 p-5"><Network className="size-5 text-primary" /><h3 className="mt-10 font-display text-xl font-semibold">Hire for capability, not just credentials.</h3><p className="mt-3 text-xs leading-5 text-muted-foreground">Publish the skills that matter and KAUSHALYA can connect you to the people building them.</p><Link href="/employer/jobs" data-testid="link-employer-create" className="mt-5 inline-flex text-xs font-bold text-primary">Post a role <ArrowRight className="ml-1 size-3.5" /></Link></div></Surface></div></EmployerFrame>;
}

export function EmployerJobsPage() {
  const jobs = useListJobs();
  const queryClient = useQueryClient();
  const create = useCreateJob();
  const [show, setShow] = useState(false);
  function submit(e: React.FormEvent<HTMLFormElement>) { e.preventDefault(); const f = new FormData(e.currentTarget); create.mutate({ data: { title: String(f.get('title')), company: String(f.get('company')), industry: String(f.get('industry')), location: String(f.get('location')), jobType: String(f.get('jobType')), experience: String(f.get('experience')), salary: String(f.get('salary')), requiredSkills: String(f.get('requiredSkills')).split(',').map((s) => s.trim()).filter(Boolean), deadline: String(f.get('deadline')) } }, { onSuccess: () => { setShow(false); queryClient.invalidateQueries({ queryKey: getListJobsQueryKey() }); } }); }
  return <EmployerFrame><PageHeader eyebrow="Employer workspace" title="Jobs and capability signals" description="Publish clear requirements. Review the opportunities connected to your workforce needs." action={<button onClick={() => setShow(!show)} data-testid="button-toggle-create-job" className="rounded-lg bg-primary px-3.5 py-2.5 text-xs font-bold text-primary-foreground">{show ? 'Close form' : 'Post a role'}</button>} />{show && <form onSubmit={submit} className="mb-5 grid gap-3 rounded-2xl border border-primary/25 bg-secondary/40 p-5 sm:grid-cols-2" data-testid="form-create-job">{['title', 'company', 'industry', 'location', 'jobType', 'experience', 'salary', 'requiredSkills', 'deadline'].map((name) => <input key={name} required name={name} placeholder={name === 'requiredSkills' ? 'Required skills, comma separated' : name[0].toUpperCase() + name.slice(1)} data-testid={`input-job-${name}`} className="h-10 rounded-lg border border-border bg-card px-3 text-sm outline-none" />)}<button disabled={create.isPending} data-testid="button-submit-job" className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-60">{create.isPending ? 'Publishing…' : 'Publish role'}</button></form>}{jobs.isLoading ? <LoadingState /> : jobs.isError ? <ErrorState onRetry={() => jobs.refetch()} /> : <Surface title="Published roles" meta={`${(jobs.data ?? []).length} roles`}><RoleList rows={jobs.data ?? []} />{!jobs.data?.length && <EmptyState title="No roles published" detail="Post your first role to connect with the regional talent signal." />}</Surface>}</EmployerFrame>;
}
function RoleList({ rows }: { rows: Array<{ id: string; title: string; company: string; location: string; salary: string; applicants: number; match: number }> }) { return <div className="space-y-2">{rows.map((job) => <div key={job.id} className="flex flex-col justify-between gap-3 rounded-xl border border-border p-4 sm:flex-row sm:items-center" data-testid={`row-employer-job-${job.id}`}><div><div className="text-sm font-semibold">{job.title}</div><div className="mt-1 text-[11px] text-muted-foreground">{job.company} · {job.location} · {job.salary}</div></div><div className="flex items-center gap-4 text-xs"><span><b>{job.applicants}</b> applicants</span><span className="rounded-full bg-accent/35 px-2 py-1 font-bold text-[#806822]">{job.match}% match</span></div></div>)}</div>; }
function Metric({ label, value, detail }: { label: string; value: string; detail: string }) { return <div className="rounded-2xl border border-card-border bg-card p-5 shadow-[var(--shadow-soft)]"><div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{label}</div><div className="mt-3 font-display text-3xl font-semibold">{value}</div><div className="mt-1 text-xs text-muted-foreground">{detail}</div></div>; }

export function InstituteDashboardPage() {
  const query = useListTrainingPrograms();
  const rows = query.data ?? [];
  return <InstituteFrame><PageHeader eyebrow="Institute workspace" title="Make impact visible." description="Track your programs from enrolment through completion and placement." action={<Link href="/institute/programs" data-testid="link-institute-programs" className="rounded-lg bg-primary px-3.5 py-2.5 text-xs font-bold text-primary-foreground">Manage programs <ArrowRight className="ml-1 inline size-3.5" /></Link>} /><div className="grid gap-4 sm:grid-cols-3"><Metric label="Active programs" value={`${rows.length}`} detail="Currently connected" /><Metric label="Learners enrolled" value={`${rows.reduce((sum, row) => sum + row.enrolled, 0)}`} detail="Across all programs" /><Metric label="Average placement" value={`${rows.length ? Math.round(rows.reduce((sum, row) => sum + row.placementRate, 0) / rows.length) : 0}%`} detail="Program-weighted view" /></div><div className="mt-5"><Surface title="Program health" meta="Outcome register"><div className="space-y-3">{rows.slice(0, 6).map((program) => <div key={program.id} className="grid gap-3 rounded-xl border border-border p-4 sm:grid-cols-[1fr_auto_auto] sm:items-center"><div><div className="text-sm font-semibold">{program.name}</div><div className="mt-1 text-[11px] text-muted-foreground">{program.enrolled} learners · {program.completionRate}% completion</div></div><div className="w-36"><ProgressBar value={program.placementRate} /><div className="mt-1 text-[10px] text-muted-foreground">{program.placementRate}% placed</div></div><div className="text-sm font-semibold text-primary">{program.impactScore} <span className="text-[10px] font-normal text-muted-foreground">impact</span></div></div>)}{query.isLoading && <LoadingState />}{query.isError && <ErrorState onRetry={() => query.refetch()} />}{!query.isLoading && !rows.length && <EmptyState title="No programs connected" detail="Publish your first program to track its employment outcomes." />}</div></Surface></div></InstituteFrame>;
}

export function InstituteProgramsPage() {
  return <InstituteFrame><PageHeader eyebrow="Institute workspace" title="Programs" description="Use the shared program register to keep training supply aligned to workforce demand." action={<Link href="/admin/program-impact" data-testid="link-program-impact" className="rounded-lg border border-border bg-card px-3.5 py-2.5 text-xs font-semibold">View impact lens <ArrowRight className="ml-1 inline size-3.5" /></Link>} /><Surface title="Program publishing" meta="Shared with government teams"><div className="grid gap-4 md:grid-cols-3"><div className="rounded-xl bg-secondary/60 p-5"><div className="text-[10px] uppercase tracking-wider text-primary">01 / Describe</div><h3 className="mt-4 font-display text-lg font-semibold">Make capability clear.</h3><p className="mt-2 text-xs leading-5 text-muted-foreground">Name the skills, duration and context learners will leave with.</p></div><div className="rounded-xl bg-[#e9eee8] p-5"><div className="text-[10px] uppercase tracking-wider text-primary">02 / Connect</div><h3 className="mt-4 font-display text-lg font-semibold">Meet the local signal.</h3><p className="mt-2 text-xs leading-5 text-muted-foreground">See where demand is growing and where your learners can respond.</p></div><div className="rounded-xl bg-accent/35 p-5"><div className="text-[10px] uppercase tracking-wider text-primary">03 / Learn</div><h3 className="mt-4 font-display text-lg font-semibold">Return with outcomes.</h3><p className="mt-2 text-xs leading-5 text-muted-foreground">Completion and placement evidence helps the whole system improve.</p></div></div><Link href="/admin/program-impact" data-testid="link-institute-open-register" className="mt-6 inline-flex items-center text-xs font-bold text-primary">Open program register <ArrowRight className="ml-1 size-3.5" /></Link></Surface></InstituteFrame>;
}
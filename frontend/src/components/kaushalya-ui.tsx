import { type ReactNode } from 'react';
import { Link, useLocation } from 'wouter';
import { ArrowRight, BarChart3, BriefcaseBusiness, Building2, Check, ChevronDown, CircleAlert, Compass, FileText, LayoutDashboard, LogOut, Menu, Network, Search, ShieldCheck, Sparkles, Target, UsersRound, X } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useLocation as useWouterLocation } from 'wouter';

export const cx = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(' ');

export function Mark({ compact = false }: { compact?: boolean }) {
  return <div className="flex items-center gap-3" data-testid="brand-kaushalya">
    <div className="relative grid size-9 place-items-center rounded-xl bg-accent text-accent-foreground shadow-sm">
      <span className="font-display text-lg font-bold">K</span>
      <span className="absolute -right-1 -top-1 size-2 rounded-full bg-primary" />
    </div>
    {!compact && <div><div className="font-display text-[15px] font-bold tracking-[.14em]">KAUSHALYA</div><div className="text-[9px] font-semibold uppercase tracking-[.18em] text-sidebar-foreground/55">workforce intelligence</div></div>}
  </div>;
}

const adminLinks = [
  { href: '/admin/dashboard', label: 'Overview', icon: LayoutDashboard },
  { href: '/admin/districts', label: 'District intelligence', icon: Network },
  { href: '/admin/skill-demand', label: 'Skill demand', icon: Target },
  { href: '/admin/predictions', label: 'Forecasts', icon: BarChart3 },
  { href: '/admin/program-impact', label: 'Program impact', icon: ShieldCheck },
];
const traineeLinks = [
  { href: '/trainee/dashboard', label: 'My overview', icon: LayoutDashboard },
  { href: '/trainee/profile', label: 'Profile', icon: UsersRound },
  { href: '/trainee/skills', label: 'My skills', icon: Target },
  { href: '/trainee/skill-gap', label: 'Skill gap', icon: Compass },
  { href: '/trainee/jobs', label: 'Job matches', icon: BriefcaseBusiness },
  { href: '/trainee/training', label: 'Training', icon: FileText },
  { href: '/trainee/recommendations', label: 'Recommendations', icon: Sparkles },
];

export function AppShell({ role, children }: { role: 'admin' | 'trainee' | 'employer' | 'institute'; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [location] = useLocation();
  const [, setLocation] = useWouterLocation();
  const { user, logout } = useAuth();
  const links = role === 'admin' ? adminLinks : role === 'trainee' ? traineeLinks : [];
  const roleLabel = role === 'admin' ? 'Government workspace' : role === 'trainee' ? 'Trainee workspace' : role === 'employer' ? 'Employer workspace' : 'Institute workspace';
  const displayName = user?.name || roleLabel;
  const initials = displayName.split(' ').map((w: string) => w[0]).join('').toUpperCase().slice(0, 2);

  function handleLogout() {
    logout();
    setLocation('/login');
  }

  return <div className="min-h-[100dvh] bg-background">
    <aside className={cx("fixed inset-y-0 left-0 z-40 flex w-[264px] flex-col bg-sidebar text-sidebar-foreground transition-transform duration-300 md:translate-x-0", open ? "translate-x-0" : "-translate-x-full")} data-testid="sidebar-navigation">
      <div className="flex h-[82px] items-center border-b border-sidebar-border px-6"><Mark /></div>
      <div className="border-b border-sidebar-border px-6 py-5">
        <div className="text-[10px] font-semibold uppercase tracking-[.18em] text-sidebar-foreground/45">Signed in as</div>
        <div className="mt-1 flex items-center justify-between">
          <div>
            <div className="text-sm font-medium">{displayName}</div>
            {user?.email && <div className="text-[10px] text-sidebar-foreground/45 truncate max-w-[160px]">{user.email}</div>}
          </div>
          <ChevronDown className="size-4 text-sidebar-foreground/45 shrink-0" />
        </div>
      </div>
      {links.length > 0 && <nav className="flex-1 space-y-1 px-3 py-5">{links.map((item) => { const Icon = item.icon; const active = location === item.href; return <Link key={item.href} href={item.href} onClick={() => setOpen(false)} data-testid={`link-${item.label.toLowerCase().replaceAll(' ', '-')}`} className={cx("group flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] transition-colors", active ? "bg-sidebar-accent text-sidebar-accent-foreground" : "text-sidebar-foreground/65 hover:bg-sidebar-accent/60 hover:text-sidebar-foreground")}><Icon className={cx("size-[17px]", active ? "text-accent" : "text-sidebar-foreground/45 group-hover:text-accent")} /><span>{item.label}</span>{active && <span className="ml-auto size-1.5 rounded-full bg-accent" />}</Link>; })}</nav>}
      <div className="border-t border-sidebar-border p-4">
        <div className="rounded-xl bg-sidebar-accent/60 p-3">
          <div className="flex items-center gap-2 text-xs font-semibold"><span className="size-2 rounded-full bg-[#78c69b]" />Data systems online</div>
          <p className="mt-1.5 text-[11px] leading-4 text-sidebar-foreground/55">Last sync 18 minutes ago across 18 districts.</p>
        </div>
        <Link href="/" data-testid="link-back-to-home" className="mt-3 block px-2 text-xs text-sidebar-foreground/45 hover:text-sidebar-foreground">Return to public site</Link>
        <button onClick={handleLogout} data-testid="button-logout" className="mt-2 flex w-full items-center gap-2 px-2 py-1.5 text-xs text-sidebar-foreground/45 hover:text-sidebar-foreground rounded-lg hover:bg-sidebar-accent/60 transition-colors">
          <LogOut className="size-3.5" />Sign out
        </button>
      </div>
    </aside>
    {open && <button aria-label="Close navigation" data-testid="button-close-navigation" onClick={() => setOpen(false)} className="fixed inset-0 z-30 bg-foreground/25 md:hidden"><X className="absolute right-5 top-5 text-background" /></button>}
    <div className="md:pl-[264px]">
      <header className="sticky top-0 z-20 flex h-[70px] items-center justify-between border-b border-border/80 bg-background/90 px-5 backdrop-blur md:px-8">
        <div className="flex items-center gap-3">
          <button onClick={() => setOpen(true)} data-testid="button-open-navigation" className="rounded-lg p-2 hover:bg-muted md:hidden"><Menu className="size-5" /></button>
          <div className="md:hidden"><Mark compact /></div>
          <span className="hidden text-xs text-muted-foreground md:block">{roleLabel} / <span className="text-foreground">{location.split('/').slice(-1)[0]?.replaceAll('-', ' ')}</span></span>
        </div>
        <div className="flex items-center gap-3">
          <button data-testid="button-global-search" className="hidden items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-xs text-muted-foreground hover:bg-muted sm:flex"><Search className="size-3.5" />Search workspace <span className="ml-3 rounded border border-border px-1.5 py-0.5 text-[10px]">⌘ K</span></button>
          <div className="grid size-8 place-items-center rounded-full bg-primary text-xs font-bold text-primary-foreground" data-testid="avatar-user" title={displayName}>{initials}</div>
        </div>
      </header>
      <main>{children}</main>
    </div>
  </div>;
}

export function PublicHeader() {
  const [open, setOpen] = useState(false);
  return <header className="absolute left-0 right-0 top-0 z-20"><div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 lg:px-8"><Link href="/" data-testid="link-public-logo"><Mark /></Link><nav className="hidden items-center gap-7 text-sm text-foreground/65 md:flex"><Link href="/about" data-testid="link-about">About</Link><Link href="/how-it-works" data-testid="link-how-it-works">How it works</Link><Link href="/login" data-testid="link-public-login" className="rounded-lg border border-border bg-card/60 px-4 py-2 font-semibold text-foreground hover:bg-card">Sign in</Link><Link href="/register" data-testid="link-public-register" className="rounded-lg bg-primary px-4 py-2 font-semibold text-primary-foreground hover:bg-primary/90">Open workspace <ArrowRight className="ml-1 inline size-3.5" /></Link></nav><button onClick={() => setOpen(!open)} data-testid="button-public-menu" className="rounded-lg p-2 md:hidden">{open ? <X /> : <Menu />}</button></div>{open && <div className="mx-5 rounded-2xl border border-border bg-card p-3 shadow-lg md:hidden"><Link href="/about" className="block rounded-lg px-3 py-2.5 text-sm" data-testid="mobile-link-about">About</Link><Link href="/how-it-works" className="block rounded-lg px-3 py-2.5 text-sm" data-testid="mobile-link-how-it-works">How it works</Link><Link href="/login" className="mt-2 block rounded-lg bg-muted px-3 py-2.5 text-sm font-semibold" data-testid="mobile-link-login">Sign in</Link></div>}</header>;
}

export function PageHeader({ eyebrow, title, description, action }: { eyebrow: string; title: string; description?: string; action?: ReactNode }) {
  return <div className="mb-7 flex flex-col justify-between gap-4 border-b border-border/80 pb-6 sm:flex-row sm:items-end"><div><div className="mb-2 text-[10px] font-bold uppercase tracking-[.19em] text-primary">{eyebrow}</div><h1 className="font-display text-3xl font-semibold tracking-[-.04em] text-foreground md:text-4xl">{title}</h1>{description && <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{description}</p>}</div>{action}</div>;
}

export function Surface({ children, className, title, meta }: { children: ReactNode; className?: string; title?: string; meta?: string }) {
  return <section className={cx("rounded-2xl border border-card-border bg-card p-5 shadow-[var(--shadow-soft)]", className)}>{title && <div className="mb-5 flex items-center justify-between"><h2 className="font-display text-[15px] font-semibold">{title}</h2>{meta && <span className="text-[11px] text-muted-foreground">{meta}</span>}</div>}{children}</section>;
}

export function KpiCard({ label, value, change, detail, trend, index = 0 }: { label: string; value: string; change?: string; detail?: string; trend?: string; index?: number }) {
  const positive = trend !== 'down';
  return <div className="animate-rise rounded-2xl border border-card-border bg-card p-5 shadow-[var(--shadow-soft)]" style={{ animationDelay: `${index * 70}ms` }} data-testid={`card-kpi-${label.toLowerCase().replaceAll(' ', '-')}`}><div className="flex items-start justify-between"><div className="text-[11px] font-semibold uppercase tracking-[.12em] text-muted-foreground">{label}</div><span className={cx("size-2 rounded-full", positive ? "bg-[#69ae87]" : "bg-[#d77a63]")} /></div><div className="mt-4 flex items-end gap-2"><div className="font-display text-3xl font-semibold tracking-[-.05em]">{value}</div>{change && <div className={cx("mb-1 text-xs font-semibold", positive ? "text-[#317954]" : "text-[#b34e41]")}>{change}</div>}</div>{detail && <div className="mt-1 text-xs text-muted-foreground">{detail}</div>}</div>;
}

export function LoadingState({ label = 'Syncing intelligence' }: { label?: string }) {
  return <div className="space-y-4" data-testid="loading-state"><div className="h-4 w-32 animate-pulse rounded bg-muted" /><div className="h-24 animate-pulse rounded-2xl bg-muted/70" /><div className="h-24 animate-pulse rounded-2xl bg-muted/60" /><p className="text-center text-xs text-muted-foreground">{label}</p></div>;
}

export function ErrorState({ onRetry }: { onRetry?: () => void }) {
  return <div className="flex min-h-[240px] flex-col items-center justify-center rounded-2xl border border-destructive/25 bg-destructive/5 p-8 text-center" data-testid="error-state"><CircleAlert className="mb-3 size-7 text-destructive" /><h3 className="font-display font-semibold">Intelligence is temporarily unavailable</h3><p className="mt-1 max-w-sm text-xs leading-5 text-muted-foreground">The data service did not respond. Your workspace is safe; try the sync again in a moment.</p>{onRetry && <button onClick={onRetry} data-testid="button-retry" className="mt-4 rounded-lg bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground">Retry connection</button>}</div>;
}

export function EmptyState({ title, detail }: { title: string; detail: string }) {
  return <div className="flex min-h-[210px] flex-col items-center justify-center rounded-2xl border border-dashed border-border p-8 text-center" data-testid="empty-state"><div className="mb-3 grid size-10 place-items-center rounded-full bg-secondary text-primary"><Compass className="size-5" /></div><h3 className="font-display font-semibold">{title}</h3><p className="mt-1 max-w-sm text-xs leading-5 text-muted-foreground">{detail}</p></div>;
}

export function ProgressBar({ value, tone = 'primary' }: { value: number; tone?: 'primary' | 'accent' | 'danger' }) {
  return <div className="h-2 overflow-hidden rounded-full bg-muted"><div className={cx("h-full rounded-full transition-all duration-700", tone === 'accent' ? "bg-accent" : tone === 'danger' ? "bg-[#d77a63]" : "bg-primary")} style={{ width: `${Math.min(100, Math.max(0, value))}%` }} /></div>;
}

export function MiniChart({ values, color = 'primary' }: { values: number[]; color?: 'primary' | 'accent' }) {
  const max = Math.max(...values, 1);
  return <div className="flex h-28 items-end gap-1.5" aria-label="trend chart" data-testid="chart-trend">{values.map((v, i) => <div key={i} className="group flex h-full flex-1 items-end" title={`${v}`}><div className={cx("w-full rounded-t-sm transition-all duration-500 group-hover:opacity-70", color === 'accent' ? "bg-accent" : "bg-primary")} style={{ height: `${Math.max(8, (v / max) * 100)}%`, animationDelay: `${i * 45}ms` }} /></div>)}</div>;
}
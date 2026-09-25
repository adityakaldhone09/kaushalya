import { useState } from 'react';
import { useLocation } from 'wouter';
import { authApi } from '@/services/api';
import { PublicHeader, ArrowRight } from '@/components/kaushalya-ui';
import { MailCheck } from 'lucide-react';

export function ForgotPasswordPage() {
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    setErrorMsg('');
    try {
      await authApi.forgotPassword(email);
      setStatus('success');
    } catch (err: any) {
      setStatus('error');
      setErrorMsg(err.message || 'Failed to send reset email.');
    }
  };

  return (
    <div className="noise min-h-[100dvh] bg-background">
      <PublicHeader />
      <div className="flex items-center justify-center pt-32 pb-20 px-5">
        <div className="w-full max-w-md">
          {status === 'success' ? (
            <div className="rounded-2xl border border-border bg-card p-8 text-center shadow-xl">
              <MailCheck className="mx-auto size-12 text-primary mb-4" />
              <h2 className="text-2xl font-semibold mb-2">Check your email</h2>
              <p className="text-sm text-muted-foreground mb-6">We've sent password reset instructions to {email}</p>
              <button onClick={() => setLocation('/login')} className="rounded-xl border border-border px-6 py-2.5 text-sm font-bold hover:bg-muted w-full">Return to Login</button>
            </div>
          ) : (
            <div className="rounded-2xl border border-border bg-card p-8 shadow-xl">
              <h2 className="text-2xl font-semibold mb-2">Reset Password</h2>
              <p className="text-sm text-muted-foreground mb-6">Enter your email address and we'll send you a link to reset your password.</p>
              <form onSubmit={submit} className="space-y-4">
                <label className="block text-xs font-semibold">Email
                  <input required type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@organisation.gov" className="mt-2 h-11 w-full rounded-xl border border-border bg-card px-3.5 text-sm font-normal outline-none focus:ring-2 focus:ring-ring" />
                </label>
                {status === 'error' && <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive">{errorMsg}</div>}
                <button disabled={status === 'loading'} className="w-full rounded-xl bg-primary py-3 text-sm font-bold text-primary-foreground shadow-lg hover:bg-primary/90 disabled:opacity-60">
                  {status === 'loading' ? 'Sending...' : 'Send reset link'}
                </button>
              </form>
              <div className="mt-6 text-center text-xs text-muted-foreground">
                Remember your password? <button onClick={() => setLocation('/login')} className="font-bold text-primary hover:underline">Sign in</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

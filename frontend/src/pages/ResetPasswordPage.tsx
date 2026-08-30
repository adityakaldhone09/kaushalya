import { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { authApi } from '@/services/api';
import { PublicHeader } from '@/components/kaushalya-ui';
import { Eye, EyeOff, CheckCircle2 } from 'lucide-react';

export function ResetPasswordPage() {
  const [, setLocation] = useLocation();
  const [token, setToken] = useState<string | null>(null);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    if (urlToken) {
      setToken(urlToken);
    } else {
      setStatus('error');
      setErrorMsg('No reset token provided in the URL.');
    }
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setStatus('loading');
    setErrorMsg('');
    try {
      await authApi.resetPassword({ token, password });
      setStatus('success');
    } catch (err: any) {
      setStatus('error');
      setErrorMsg(err.message || 'Failed to reset password.');
    }
  };

  return (
    <div className="noise min-h-[100dvh] bg-background">
      <PublicHeader />
      <div className="flex items-center justify-center pt-32 pb-20 px-5">
        <div className="w-full max-w-md">
          {status === 'success' ? (
            <div className="rounded-2xl border border-border bg-card p-8 text-center shadow-xl">
              <CheckCircle2 className="mx-auto size-12 text-primary mb-4" />
              <h2 className="text-2xl font-semibold mb-2">Password Reset</h2>
              <p className="text-sm text-muted-foreground mb-6">Your password has been successfully reset. You can now login with your new password.</p>
              <button onClick={() => setLocation('/login')} className="rounded-xl bg-primary px-6 py-2.5 text-sm font-bold text-primary-foreground w-full hover:bg-primary/90">Go to Login</button>
            </div>
          ) : (
            <div className="rounded-2xl border border-border bg-card p-8 shadow-xl">
              <h2 className="text-2xl font-semibold mb-2">Set new password</h2>
              <p className="text-sm text-muted-foreground mb-6">Enter your new password below.</p>
              <form onSubmit={submit} className="space-y-4">
                <label className="block text-xs font-semibold">New Password
                  <div className="relative mt-2">
                    <input required type={showPassword ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 8 characters" className="h-11 w-full rounded-xl border border-border bg-card px-3.5 pr-11 text-sm font-normal outline-none focus:ring-2 focus:ring-ring" />
                    <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-3 text-muted-foreground">
                      {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                    </button>
                  </div>
                </label>
                {status === 'error' && <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive">{errorMsg}</div>}
                <button disabled={status === 'loading' || !token} className="w-full rounded-xl bg-primary py-3 text-sm font-bold text-primary-foreground shadow-lg hover:bg-primary/90 disabled:opacity-60">
                  {status === 'loading' ? 'Saving...' : 'Reset Password'}
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

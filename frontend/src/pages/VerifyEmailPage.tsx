import { useEffect, useState } from 'react';
import { useLocation } from 'wouter';
import { authApi } from '@/services/api';
import { PublicHeader, LoadingState, ErrorState } from '@/components/kaushalya-ui';
import { CheckCircle2, XCircle } from 'lucide-react';

export function VerifyEmailPage() {
  const [location, setLocation] = useLocation();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');

    if (!token) {
      setStatus('error');
      setErrorMsg('No verification token provided.');
      return;
    }

    authApi.verifyEmail(token)
      .then(() => {
        setStatus('success');
      })
      .catch((err) => {
        setStatus('error');
        setErrorMsg(err.message || 'Email verification failed.');
      });
  }, []);

  return (
    <div className="noise min-h-[100dvh] bg-background">
      <PublicHeader />
      <div className="flex items-center justify-center pt-32 pb-20">
        <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 shadow-xl text-center">
          {status === 'loading' && (
            <div className="py-8">
              <LoadingState />
              <p className="mt-4 text-sm text-muted-foreground">Verifying your email...</p>
            </div>
          )}
          {status === 'success' && (
            <div className="py-8">
              <CheckCircle2 className="mx-auto size-12 text-primary mb-4" />
              <h2 className="text-2xl font-semibold mb-2">Email Verified</h2>
              <p className="text-sm text-muted-foreground mb-6">Your email has been successfully verified. You can now access your workspace.</p>
              <button onClick={() => setLocation('/login')} className="rounded-xl bg-primary px-6 py-2.5 text-sm font-bold text-primary-foreground">Go to Login</button>
            </div>
          )}
          {status === 'error' && (
            <div className="py-8">
              <XCircle className="mx-auto size-12 text-destructive mb-4" />
              <h2 className="text-2xl font-semibold mb-2">Verification Failed</h2>
              <p className="text-sm text-muted-foreground mb-6">{errorMsg}</p>
              <button onClick={() => setLocation('/login')} className="rounded-xl border border-border px-6 py-2.5 text-sm font-bold hover:bg-muted">Return to Login</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

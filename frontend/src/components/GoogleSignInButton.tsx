import { useEffect, useRef, useState } from 'react';

declare global {
  interface Window {
    google?: { accounts: { id: {
      initialize: (config: { client_id: string; callback: (response: { credential: string }) => void }) => void;
      renderButton: (element: HTMLElement, options: Record<string, unknown>) => void;
    } } };
  }
}

interface Props {
  onCredential: (credential: string) => void;
  disabled?: boolean;
}

/** Renders Google's official Identity Services control, including its official G logo. */
export function GoogleSignInButton({ onCredential, disabled }: Props) {
  const host = useRef<HTMLDivElement>(null);
  const [unavailable, setUnavailable] = useState(false);
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

  useEffect(() => {
    if (!clientId || disabled) return;
    const render = () => {
      if (!host.current || !window.google) return;
      window.google.accounts.id.initialize({ client_id: clientId, callback: ({ credential }) => onCredential(credential) });
      host.current.replaceChildren();
      window.google.accounts.id.renderButton(host.current, { theme: 'outline', size: 'large', text: 'continue_with', width: 420 });
    };
    const existing = document.querySelector<HTMLScriptElement>('script[data-google-identity]');
    if (existing) { existing.addEventListener('load', render); render(); return () => existing.removeEventListener('load', render); }
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client'; script.async = true; script.defer = true;
    script.dataset.googleIdentity = 'true'; script.onload = render; script.onerror = () => setUnavailable(true);
    document.head.appendChild(script);
  }, [clientId, disabled, onCredential]);

  if (!clientId || unavailable) return null;
  return <div className={disabled ? 'pointer-events-none opacity-60' : ''}><div ref={host} className="flex justify-center" /></div>;
}

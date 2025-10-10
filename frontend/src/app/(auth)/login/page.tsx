'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Logo } from '@/components/logo';
import Swal from 'sweetalert2';
import { login } from '@/lib/api/auth';
import Cookies from 'js-cookie';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionExpired = searchParams.get('sessionExpired');

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (sessionExpired) {
      Swal.fire({
        icon: 'warning',
        title: 'Oturumunuzun süresi doldu!',
        text: 'Lütfen tekrar giriş yapın.',
        timer: 2000,
        timerProgressBar: true,
      });

      // Query param'ı temizle
      const url = new URL(window.location.href);
      url.searchParams.delete('sessionExpired');
      window.history.replaceState(null, '', url.toString());
    }
  }, [sessionExpired]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const res = await login({ username, password });

      if (!res.ok) {
        const err = await res.json();
        const msg =
          err?.detail && Array.isArray(err.detail) && err.detail[0]?.msg
            ? err.detail[0].msg
            : err?.detail || 'Giriş başarısız!';

        await Swal.fire({
          icon: 'warning',
          title: 'Uyarı!',
          text: msg,
          confirmButtonText: 'Tamam',
        });

        throw new Error(msg);
      }

      const data = await res.json();
      console.log('Login başarılı, token:', data);

      sessionStorage.setItem('access_token', data.access_token);
      sessionStorage.setItem('token_type', data.token_type);
      Cookies.set('access_token', data.access_token, { expires: 1 });

      await Swal.fire({
        icon: 'success',
        title: 'Başarılı!',
        text: 'Giriş başarılı!',
        timer: 2000,
        showConfirmButton: false,
        timerProgressBar: true,
      });

      router.push('/jobs');
    } catch (err: any) {
      const msg =
        err?.message ||
        (err?.detail && Array.isArray(err.detail) && err.detail[0]?.msg
          ? err.detail[0].msg
          : 'Giriş başarısız!');
      setError(msg);
      console.error('Login error:', err);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Card className="mx-auto w-full max-w-sm">
        <CardHeader className="items-center text-center">
          <Logo />
          <CardTitle className="mt-2 font-headline text-2xl">
            SÖBE İK Yönetim Sistemi Giriş
          </CardTitle>
          <CardDescription>
            Hesabınıza erişmek için kullanıcı adınızı ve şifrenizi girin.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="username">Kullanıcı Adı</Label>
              <Input
                id="username"
                type="text"
                placeholder="kullaniciadi"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">Şifre</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && <p className="text-sm text-red-500">{error}</p>}
            <Button type="submit" className="w-full">
              Giriş Yap
            </Button>
          </form>
          <Button
            onClick={() => router.push('/signup')}
            className="mt-2 w-full bg-purple-600 text-white hover:bg-purple-700"
          >
            Kayıt Ol
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

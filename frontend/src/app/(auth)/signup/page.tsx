'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
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
import { signup } from '@/lib/api/auth';
import Swal from 'sweetalert2';

export default function SignupPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('HR');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const res = await signup({ username, email, role, password });

      if (!res.ok) {
        const err = await res.json();
        const msg =
          err?.detail && Array.isArray(err.detail) && err.detail[0]?.msg
            ? err.detail[0].msg
            : err?.detail || 'Kayıt başarısız!';

        await Swal.fire({
          icon: 'warning',
          title: 'Uyarı!',
          text: msg,
          confirmButtonText: 'Tamam',
        });

        throw new Error(msg);
      }

      await Swal.fire({
        icon: 'success',
        title: 'Başarılı!',
        text: 'Kayıt işleminiz tamamlandı!',
        confirmButtonText: 'Giriş Yap',
      });

      router.push('/login');
    } catch (err: any) {
      const msg =
        err?.message ||
        (err?.detail && Array.isArray(err.detail) && err.detail[0]?.msg
          ? err.detail[0].msg
          : 'Kayıt başarısız!');
      setError(msg);
      console.error('Signup error:', err);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Card className="mx-auto w-full max-w-sm">
        <CardHeader className="items-center text-center">
          <Logo />
          <CardTitle className="mt-2 font-headline text-2xl">
            SÖBE İK Yönetim Sistemi Kayıt Ol
          </CardTitle>
          <CardDescription>
            Hesabınızı oluşturmak için bilgileri girin.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSignup} className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="username">Kullanıcı Adı</Label>
              <Input
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="email">E-posta</Label>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
              Kayıt Ol
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

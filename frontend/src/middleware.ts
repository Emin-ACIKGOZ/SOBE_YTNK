import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Next.js için temel kimlik doğrulama ara katman yazılımı (middleware).
 * Kullanıcının oturum açma durumunu kontrol eder ve rotaları buna göre yönlendirir.
 *
 * * İşleyiş:
 *
 * 1. Tarayıcı çerezlerinden 'access_token' değerini alır.
 *
 * 2. Kullanıcı '/login' veya '/signup' rotalarına erişmeye çalışıyorsa:
 * - Eğer bir belirteç (token) varsa, '/jobs' sayfasına yönlendirir (zaten oturum açık).
 * - Belirteç yoksa, normal akışa devam eder (giriş yapmaya izin verir).
 *
 * 3. Diğer tüm korumalı rotalar için:
 * - Eğer belirteç yoksa, kullanıcıyı '/login' sayfasına `sessionExpired=true` parametresiyle yönlendirir.
 *
 * 4. Belirteç varsa, normal akışa devam eder.
 *
 * * @param req Gelen Next.js isteği.
 * @returns Yönlendirme yanıtı (NextResponse.redirect) veya normal akışa devam etme (NextResponse.next).
 */
export function middleware(req: NextRequest) {
  const token = req.cookies.get('access_token')?.value || null;

  if (
    req.nextUrl.pathname.startsWith('/login') ||
    req.nextUrl.pathname.startsWith('/signup')
  ) {
    if (token) {
      return NextResponse.redirect(new URL('/jobs', req.url));
    }
    return NextResponse.next();
  }

  if (!token) {
    const loginUrl = new URL('/login', req.url);
    loginUrl.searchParams.set('sessionExpired', 'true');
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

/**
 * Bu ara katman yazılımının uygulanacağı yolları (rotaları) tanımlar.
 */
export const config = {
  /**
   * '/jobs' altındaki tüm yollar (recursive), '/login' ve '/signup' yolları ile eşleşir.
   */
  matcher: ['/jobs/:path*', '/login', '/signup'],
};

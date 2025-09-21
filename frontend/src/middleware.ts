// src/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(req: NextRequest) {
    const token = req.cookies.get("access_token")?.value || null;

    if (req.nextUrl.pathname.startsWith("/login") || req.nextUrl.pathname.startsWith("/signup")) {
        if (token) {
            return NextResponse.redirect(new URL("/jobs", req.url));
        }
        return NextResponse.next();
    }

    if (!token) {
        const loginUrl = new URL("/login", req.url);
        loginUrl.searchParams.set("sessionExpired", "true");
        return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
}

export const config = {
    matcher: ["/jobs/:path*", "/login", "/signup"],
};

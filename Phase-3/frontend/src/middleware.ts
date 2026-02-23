import { NextRequest, NextResponse } from "next/server";

// Protected dashboard routes
const PROTECTED = [
  "/chatbot",
  "/analytics",
  "/settings",
  "/history",
  "/help",
];


export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check for Better Auth session cookie
  const sessionToken =
    request.cookies.get("better-auth.session_token")?.value ??
    request.cookies.get("__Secure-better-auth.session_token")?.value;

  const isProtected = PROTECTED.some((p) => pathname.startsWith(p));
  // Unauthenticated user tries to access protected route → redirect to signin
  if (isProtected && !sessionToken) {
    const url = request.nextUrl.clone();
    url.pathname = "/signin";
    url.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|public).*)",
  ],
};

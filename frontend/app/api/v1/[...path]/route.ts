import { NextRequest, NextResponse } from "next/server";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

async function proxy(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const configuredUrl =
    process.env.FORGEGUARD_API_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://127.0.0.1:8000/api/v1";

  let target: URL;
  try {
    const base = new URL(configuredUrl);
    if (base.protocol !== "http:" && base.protocol !== "https:") {
      throw new Error("Unsupported protocol");
    }
    const basePath = base.pathname.replace(/\/$/, "");
    target = new URL(
      `${basePath}/${path.map((part) => encodeURIComponent(part)).join("/")}${request.nextUrl.search}`,
      base.origin,
    );
  } catch {
    return NextResponse.json({ detail: "Invalid ForgeGuard API URL configuration" }, { status: 500 });
  }

  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers: request.headers.get("content-type")
        ? { "Content-Type": request.headers.get("content-type") as string }
        : undefined,
      body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.text(),
      cache: "no-store",
    });
    const responseBody = await upstream.text();
    return new NextResponse(responseBody, {
      status: upstream.status,
      headers: {
        "Content-Type": upstream.headers.get("content-type") ?? "application/json",
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return NextResponse.json(
      { detail: "ForgeGuard backend is unavailable. Start the API and retry." },
      { status: 502 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;

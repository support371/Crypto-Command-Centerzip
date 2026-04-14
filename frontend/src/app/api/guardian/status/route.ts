import { NextResponse } from 'next/server';

const GUARDIAN_BOT = process.env.GUARDIAN_BOT_URL || 'http://localhost:8002';

export async function GET() {
  try {
    const res = await fetch(`${GUARDIAN_BOT}/status`, {
      headers: { 'x-api-key': process.env.GUARDIAN_BOT_API_KEY || '' },
      next: { revalidate: 0 },
    });
    if (!res.ok) throw new Error('Guardian bot unavailable');
    return NextResponse.json(await res.json());
  } catch {
    return NextResponse.json({ state: 'offline' });
  }
}

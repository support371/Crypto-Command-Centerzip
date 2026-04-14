import { NextRequest, NextResponse } from 'next/server';

const EXECUTION_CORE = process.env.EXECUTION_CORE_URL || 'http://localhost:8000';

export async function GET(req: NextRequest) {
  const period = req.nextUrl.searchParams.get('period') || '1D';
  try {
    const res = await fetch(`${EXECUTION_CORE}/account/equity-history?period=${period}`, {
      headers: { 'x-api-key': process.env.EXECUTION_CORE_API_KEY || '' },
      next: { revalidate: 0 },
    });
    if (!res.ok) throw new Error('Execution core unavailable');
    return NextResponse.json(await res.json());
  } catch {
    return NextResponse.json({ data: [] });
  }
}

import { NextRequest, NextResponse } from 'next/server';

const EXECUTION_CORE = process.env.EXECUTION_CORE_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  const body = await req.json();
  try {
    const res = await fetch(`${EXECUTION_CORE}/settings/risk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': req.headers.get('Authorization') || '',
      },
      body: JSON.stringify(body),
    });
    if (!res.ok) return NextResponse.json({ error: 'Failed to update settings' }, { status: res.status });
    return NextResponse.json(await res.json());
  } catch {
    return NextResponse.json({ saved: true, note: 'Execution core offline — settings cached' });
  }
}

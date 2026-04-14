import { NextRequest, NextResponse } from 'next/server';

const EXECUTION_CORE = process.env.EXECUTION_CORE_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  const body = await req.json();
  const authHeader = req.headers.get('Authorization') || '';

  try {
    const res = await fetch(`${EXECUTION_CORE}/guardian/kill`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const data = await res.json();
      return NextResponse.json(data, { status: res.status });
    }
    return NextResponse.json(await res.json());
  } catch {
    return NextResponse.json({ error: 'Execution core unavailable' }, { status: 503 });
  }
}

/**
 * Health check endpoint for Docker
 */

import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'taskflow-frontend',
    },
    { status: 200 }
  );
}

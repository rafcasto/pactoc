import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Return mock stats
    return NextResponse.json({
      stats: {
        total: 0,
        pending: 0,
        completed: 0,
        expired: 0
      }
    });
  } catch (error) {
    console.error('Error fetching invitation stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch stats' },
      { status: 500 }
    );
  }
}

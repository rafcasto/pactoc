import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  try {
    // For now, return empty data
    return NextResponse.json({
      invitations: [],
      total: 0
    });
  } catch (error) {
    console.error('Error fetching invitations:', error);
    return NextResponse.json(
      { error: 'Failed to fetch invitations' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('Creating invitation:', body);
    
    // For now, return a mock response
    return NextResponse.json({
      success: true,
      invitation: {
        id: Math.random().toString(36).substr(2, 9),
        email: body.email,
        first_name: body.first_name,
        last_name: body.last_name,
        status: 'pending',
        created_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        public_link: `https://example.com/invitation/${Math.random().toString(36).substr(2, 9)}`
      }
    });
  } catch (error) {
    console.error('Error creating invitation:', error);
    return NextResponse.json(
      { error: 'Failed to create invitation' },
      { status: 500 }
    );
  }
}

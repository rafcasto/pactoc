import { NextRequest, NextResponse } from 'next/server';
import { verifyRecaptcha } from '@/lib/recaptcha/verify';

export async function POST(request: NextRequest) {
  try {
    const { token } = await request.json();

    if (!token) {
      return NextResponse.json(
        { success: false, error: 'reCAPTCHA token is required' },
        { status: 400 }
      );
    }

    const result = await verifyRecaptcha(token);

    return NextResponse.json(result);
  } catch (error) {
    console.error('reCAPTCHA verification error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
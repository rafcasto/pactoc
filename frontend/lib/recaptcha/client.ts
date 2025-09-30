import { RECAPTCHA_CONFIG } from './config';

/**
 * Client-side reCAPTCHA utilities
 */

/**
 * Check if reCAPTCHA is properly configured
 */
export function isRecaptchaConfigured(): boolean {
  return !!RECAPTCHA_CONFIG.siteKey;
}

/**
 * Verify reCAPTCHA token with the backend API
 */
export async function verifyRecaptchaToken(token: string): Promise<{
  success: boolean;
  score?: number;
  error?: string;
}> {
  try {
    const response = await fetch('/api/recaptcha/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('reCAPTCHA verification failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}
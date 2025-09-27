interface RecaptchaVerificationResponse {
    success: boolean;
    score?: number;
    action?: string;
    challenge_ts?: string;
    hostname?: string;
    'error-codes'?: string[];
  }
  
  export async function verifyRecaptcha(token: string): Promise<{
    success: boolean;
    score: number;
    error?: string;
  }> {
    const secretKey = process.env.RECAPTCHA_SECRET_KEY;
  
    if (!secretKey) {
      return { success: true, score: 1.0 }; // Allow if no secret key (dev mode)
    }
  
    try {
      const response = await fetch('https://www.google.com/recaptcha/api/siteverify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `secret=${secretKey}&response=${token}`,
      });
  
      const data: RecaptchaVerificationResponse = await response.json();
  
      if (!data.success) {
        return {
          success: false,
          score: 0,
          error: `reCAPTCHA verification failed: ${data['error-codes']?.join(', ') || 'Unknown error'}`,
        };
      }
  
      const score = data.score || 0;
      const threshold = 0.5; // Adjust this threshold as needed (0.0-1.0)
  
      return {
        success: score >= threshold,
        score,
        error: score < threshold ? 'reCAPTCHA score too low' : undefined,
      };
    } catch (error) {
      console.error('reCAPTCHA verification error:', error);
      return {
        success: false,
        score: 0,
        error: 'reCAPTCHA verification service unavailable',
      };
    }
  }
  
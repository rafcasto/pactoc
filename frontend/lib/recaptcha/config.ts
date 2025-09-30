// reCAPTCHA Configuration
export const RECAPTCHA_CONFIG = {
  // Site key for client-side reCAPTCHA (public)
  siteKey: process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY,
  
  // Secret key for server-side verification (private)
  secretKey: process.env.RECAPTCHA_SECRET_KEY,
  
  // Minimum score threshold for reCAPTCHA v3 (0.0 to 1.0)
  minScore: 0.5,
  
  // reCAPTCHA API endpoint
  verifyUrl: 'https://www.google.com/recaptcha/api/siteverify',
} as const;
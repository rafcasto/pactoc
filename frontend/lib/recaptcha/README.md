# reCAPTCHA Setup Guide

This application uses Google reCAPTCHA v3 to protect forms from spam and abuse.

## Required Environment Variables

Add these variables to your `.env.local` file:

```bash
# reCAPTCHA Configuration
NEXT_PUBLIC_RECAPTCHA_SITE_KEY=your-site-key-here
RECAPTCHA_SECRET_KEY=your-secret-key-here
```

## How to Get reCAPTCHA Keys

1. Go to the [Google reCAPTCHA Admin Console](https://www.google.com/recaptcha/admin)
2. Click "Create" to register a new site
3. Choose "reCAPTCHA v3" as the type
4. Add your domain(s):
   - For development: `localhost`
   - For production: your actual domain
5. Accept the terms and submit
6. Copy the **Site Key** to `NEXT_PUBLIC_RECAPTCHA_SITE_KEY`
7. Copy the **Secret Key** to `RECAPTCHA_SECRET_KEY`

## Environment Variables Explanation

- `NEXT_PUBLIC_RECAPTCHA_SITE_KEY`: Public key used on the client-side to render reCAPTCHA
- `RECAPTCHA_SECRET_KEY`: Private key used on the server-side to verify reCAPTCHA tokens

## Current Implementation

- **Client-side**: Uses `react-google-recaptcha-v3` library
- **Provider**: `lib/recaptcha/provider.tsx` wraps the app with reCAPTCHA context
- **Hook**: `lib/hooks/useRecaptcha.ts` provides easy access to reCAPTCHA functions
- **Verification**: `lib/recaptcha/verify.ts` handles server-side token verification
- **Forms**: Login and signup forms use reCAPTCHA protection

## Testing

If reCAPTCHA keys are not configured, the forms will still work but without reCAPTCHA protection. Check the browser console for warnings about missing keys.
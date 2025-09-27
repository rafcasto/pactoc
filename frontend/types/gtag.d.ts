// types/gtag.d.ts
declare global {
    interface Window {
      dataLayer: Record<string, unknown>[];
      gtag: (
        command: 'config' | 'event' | 'js',
        targetId: string | Date,
        config?: Record<string>
      ) => void;
    }
  }
  
  export {};
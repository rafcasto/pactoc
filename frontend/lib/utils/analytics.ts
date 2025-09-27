export const GA_TRACKING_ID = 'G-CLSJSKPFGE';
// Track page views
export const pageview = (url?: string) => {
    // Only run on client-side after hydration
    if (typeof window !== 'undefined' && window.gtag && document.readyState === 'complete') {
      window.gtag('config', GA_TRACKING_ID, {
        page_location: url || window.location.href,
        page_title: document.title
      });
    }
  };
  
  // Define event parameter types
  interface EventParameters {
    event_category?: string;
    event_label?: string;
    value?: number;
    custom_parameter?: string;
    page_location?: string;
    page_title?: string;
    currency?: string;
    [key: string]: string | number | boolean | undefined;
  }
  
  // Track custom events
  export const event = (
    eventName: string,
    parameters?: EventParameters
  ) => {
    // Debug logging in development
    if (process.env.NODE_ENV === 'development') {
      console.log('🔍 GA Event:', eventName, parameters);
    }
  
    // Only run on client-side after hydration
    if (typeof window !== 'undefined' && window.gtag && document.readyState === 'complete') {
      window.gtag('event', eventName, parameters);
    }
  };
  
  // Helper functions for common events
  export const trackButtonClick = (buttonName: string) => {
    event('button_click', {
      event_category: 'engagement',
      event_label: buttonName
    });
  };
  
  export const trackFormSubmit = (formName: string) => {
    event('form_submit', {
      event_category: 'form',
      event_label: formName
    });
  };
  
  export const trackWhatsAppClick = (location: string) => {
    event('whatsapp_click', {
      event_category: 'conversion',
      event_label: location
    });
  };
  
  export const trackDemoClick = () => {
    event('demo_click', {
      event_category: 'engagement',
      event_label: 'watch_demo'
    });
  };
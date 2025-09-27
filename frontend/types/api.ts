export interface ApiResponse<T = any> {
    success: boolean;
    message: string;
    data?: T;
    timestamp: string;
  }
  
  export interface ApiError {
    success: false;
    message: string;
    error_code?: string;
    timestamp: string;
  }
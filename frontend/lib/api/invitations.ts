/**
 * Authenticated API client for invitation operations
 * Provides consistent authentication and error handling across the app
 */

interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface InvitationData {
  email: string;
  first_name?: string;
  last_name?: string;
}

interface WorkflowInvitationData {
  email: string;
  patient_name: string;
}

interface InvitationStats {
  total: number;
  pending: number;
  completed: number;
  expired: number;
}

class InvitationAPI {
  private static getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  private static async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ 
        error: `HTTP ${response.status}: ${response.statusText}` 
      }));
      throw new Error(error.error || error.message || `HTTP ${response.status}`);
    }
    return response.json();
  }

  private static logAPICall(method: string, url: string, data?: any) {
    console.log(`🔗 API ${method} ${url}`, data ? { data } : '');
  }

  /**
   * Get all invitations
   */
  static async getAll() {
    this.logAPICall('GET', '/api/invitations');
    const response = await fetch('/api/invitations', {
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse(response);
  }

  /**
   * Get invitation statistics
   */
  static async getStats(): Promise<{ stats: InvitationStats }> {
    this.logAPICall('GET', '/api/invitations/stats');
    const response = await fetch('/api/invitations/stats', {
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse(response);
  }

  /**
   * Create a standard invitation
   */
  static async create(data: InvitationData) {
    this.logAPICall('POST', '/api/invitations', data);
    const response = await fetch('/api/invitations', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  /**
   * Create a workflow invitation (for meal plans)
   */
  static async createWorkflow(data: WorkflowInvitationData) {
    this.logAPICall('POST', '/api/workflow/invitations', data);
    const response = await fetch('/api/workflow/invitations', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  /**
   * Resend an invitation
   */
  static async resend(invitationId: string) {
    this.logAPICall('POST', `/api/invitations/${invitationId}/resend`);
    const response = await fetch(`/api/invitations/${invitationId}/resend`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse(response);
  }

  /**
   * Regenerate invitation link
   */
  static async regenerate(invitationId: string) {
    this.logAPICall('POST', `/api/invitations/${invitationId}/regenerate`);
    const response = await fetch(`/api/invitations/${invitationId}/regenerate`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse(response);
  }

  /**
   * Cancel/delete an invitation
   */
  static async cancel(invitationId: string) {
    this.logAPICall('DELETE', `/api/invitations/${invitationId}`);
    const response = await fetch(`/api/invitations/${invitationId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse(response);
  }

  /**
   * Copy text to clipboard with user feedback
   */
  static async copyToClipboard(text: string, description = 'Link'): Promise<void> {
    try {
      await navigator.clipboard.writeText(text);
      console.log(`📋 ${description} copied to clipboard`);
    } catch (error) {
      console.error(`Failed to copy ${description.toLowerCase()}:`, error);
      throw new Error(`Failed to copy ${description.toLowerCase()}`);
    }
  }
}

export default InvitationAPI;
export type { InvitationData, WorkflowInvitationData, InvitationStats };

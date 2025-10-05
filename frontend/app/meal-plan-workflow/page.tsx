'use client';

import React, { useState, useEffect } from 'react';
import { 
  Plus, Search, Users, Clock, CheckCircle, Eye, Mail, 
  ExternalLink, Copy, Send, User, Calendar, FileText, Loader2
} from 'lucide-react';

interface WorkflowInvitation {
  invitation_id: number;
  patient_name: string;
  email: string;
  sent_at?: string;
  submitted_at?: string;
  approved_at?: string;
  expires_at?: string;
  patient_id?: number;
  meal_plan_id?: number;
  plan_name?: string;
  start_date?: string;
  end_date?: string;
  dynamic_link: string;
}

interface DashboardData {
  pending_review: WorkflowInvitation[];
  approved_plans: WorkflowInvitation[];
  pending_invitations: WorkflowInvitation[];
}

export default function MealPlanWorkflowPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    pending_review: [],
    approved_plans: [],
    pending_invitations: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal states
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [selectedInvitation, setSelectedInvitation] = useState<WorkflowInvitation | null>(null);
  
  // Form states
  const [inviteForm, setInviteForm] = useState({
    email: '',
    patient_name: '',
    submitting: false
  });
  
  const [approveForm, setApproveForm] = useState({
    plan_name: '',
    notes: '',
    submitting: false
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/workflow/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        setDashboardData(data.data);
      } else {
        setError(data.error || 'Failed to load dashboard data');
      }
      
    } catch (error) {
      console.error('Error loading dashboard:', error);
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSendInvitation = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inviteForm.email || !inviteForm.patient_name) {
      setError('Email and patient name are required');
      return;
    }
    
    setInviteForm(prev => ({ ...prev, submitting: true }));
    setError(null);
    
    try {
      const response = await fetch('/api/workflow/invitations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          email: inviteForm.email,
          patient_name: inviteForm.patient_name,
        }),
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        setShowInviteModal(false);
        setInviteForm({ email: '', patient_name: '', submitting: false });
        await loadDashboardData();
      } else {
        setError(data.error || 'Failed to send invitation');
      }
      
    } catch (error) {
      console.error('Error sending invitation:', error);
      setError('Connection error. Please try again.');
    } finally {
      setInviteForm(prev => ({ ...prev, submitting: false }));
    }
  };

  const handleApprove = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedInvitation) return;
    
    setApproveForm(prev => ({ ...prev, submitting: true }));
    setError(null);
    
    try {
      const response = await fetch(`/api/workflow/approve/${selectedInvitation.invitation_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          plan_name: approveForm.plan_name || `Weekly Plan - ${selectedInvitation.patient_name}`,
          notes: approveForm.notes,
        }),
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        setShowApproveModal(false);
        setSelectedInvitation(null);
        setApproveForm({ plan_name: '', notes: '', submitting: false });
        await loadDashboardData();
      } else {
        setError(data.error || 'Failed to approve meal plan');
      }
      
    } catch (error) {
      console.error('Error approving meal plan:', error);
      setError('Connection error. Please try again.');
    } finally {
      setApproveForm(prev => ({ ...prev, submitting: false }));
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const filteredData = {
    pending_review: dashboardData.pending_review.filter(item =>
      item.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.email.toLowerCase().includes(searchTerm.toLowerCase())
    ),
    approved_plans: dashboardData.approved_plans.filter(item =>
      item.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.email.toLowerCase().includes(searchTerm.toLowerCase())
    ),
    pending_invitations: dashboardData.pending_invitations.filter(item =>
      item.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.email.toLowerCase().includes(searchTerm.toLowerCase())
    ),
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-light text-gray-900">Meal Plan Workflow</h1>
              <p className="text-gray-600 mt-1">Manage patient invitations and meal plan approvals</p>
            </div>
            <button
              onClick={() => setShowInviteModal(true)}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              <Plus className="w-4 h-4 mr-2" />
              Send Invitation
            </button>
          </div>
          
          {/* Search */}
          <div className="mt-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search patients..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full max-w-md border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Pending Review</p>
                <p className="text-2xl font-semibold text-gray-900">{dashboardData.pending_review.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Approved Plans</p>
                <p className="text-2xl font-semibold text-gray-900">{dashboardData.approved_plans.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Pending Invitations</p>
                <p className="text-2xl font-semibold text-gray-900">{dashboardData.pending_invitations.length}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {/* Pending Review Section */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Pending Review</h2>
            {filteredData.pending_review.length > 0 ? (
              <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                <div className="divide-y divide-gray-200">
                  {filteredData.pending_review.map((invitation) => (
                    <div key={invitation.invitation_id} className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="p-2 bg-yellow-100 rounded-lg">
                            <User className="w-6 h-6 text-yellow-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{invitation.patient_name}</h3>
                            <p className="text-sm text-gray-500">{invitation.email}</p>
                            <p className="text-xs text-gray-400">
                              Submitted: {invitation.submitted_at ? new Date(invitation.submitted_at).toLocaleDateString() : 'N/A'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => window.open(invitation.dynamic_link, '_blank')}
                            className="inline-flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </button>
                          <button
                            onClick={() => copyToClipboard(invitation.dynamic_link)}
                            className="inline-flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                          >
                            <Copy className="w-4 h-4 mr-1" />
                            Copy Link
                          </button>
                          <button
                            onClick={() => {
                              setSelectedInvitation(invitation);
                              setApproveForm({
                                plan_name: `Weekly Plan - ${invitation.patient_name}`,
                                notes: '',
                                submitting: false
                              });
                              setShowApproveModal(true);
                            }}
                            className="inline-flex items-center px-3 py-1 text-sm bg-green-600 text-white rounded-md hover:bg-green-700"
                          >
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Approve
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No patients pending review</p>
              </div>
            )}
          </section>

          {/* Approved Plans Section */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Approved Meal Plans</h2>
            {filteredData.approved_plans.length > 0 ? (
              <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                <div className="divide-y divide-gray-200">
                  {filteredData.approved_plans.map((invitation) => (
                    <div key={invitation.invitation_id} className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="p-2 bg-green-100 rounded-lg">
                            <CheckCircle className="w-6 h-6 text-green-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{invitation.patient_name}</h3>
                            <p className="text-sm text-gray-500">{invitation.plan_name}</p>
                            <p className="text-xs text-gray-400">
                              {invitation.start_date && invitation.end_date 
                                ? `${new Date(invitation.start_date).toLocaleDateString()} - ${new Date(invitation.end_date).toLocaleDateString()}`
                                : 'Date range not available'
                              }
                            </p>
                            <p className="text-xs text-gray-400">
                              Approved: {invitation.approved_at ? new Date(invitation.approved_at).toLocaleDateString() : 'N/A'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => window.open(invitation.dynamic_link, '_blank')}
                            className="inline-flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                          >
                            <ExternalLink className="w-4 h-4 mr-1" />
                            View Plan
                          </button>
                          <button
                            onClick={() => copyToClipboard(invitation.dynamic_link)}
                            className="inline-flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                          >
                            <Copy className="w-4 h-4 mr-1" />
                            Copy Link
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <CheckCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No approved meal plans yet</p>
              </div>
            )}
          </section>

          {/* Pending Invitations Section */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Pending Invitations</h2>
            {filteredData.pending_invitations.length > 0 ? (
              <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                <div className="divide-y divide-gray-200">
                  {filteredData.pending_invitations.map((invitation) => (
                    <div key={invitation.invitation_id} className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="p-2 bg-blue-100 rounded-lg">
                            <Mail className="w-6 h-6 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{invitation.patient_name}</h3>
                            <p className="text-sm text-gray-500">{invitation.email}</p>
                            <p className="text-xs text-gray-400">
                              Sent: {invitation.sent_at ? new Date(invitation.sent_at).toLocaleDateString() : 'N/A'}
                            </p>
                            <p className="text-xs text-gray-400">
                              Expires: {invitation.expires_at ? new Date(invitation.expires_at).toLocaleDateString() : 'N/A'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => copyToClipboard(invitation.dynamic_link)}
                            className="inline-flex items-center px-3 py-1 text-sm border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                          >
                            <Copy className="w-4 h-4 mr-1" />
                            Copy Link
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No pending invitations</p>
              </div>
            )}
          </section>
        </div>

        {/* Send Invitation Modal */}
        {showInviteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl shadow-lg max-w-md w-full p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Send Meal Plan Invitation</h2>
              
              <form onSubmit={handleSendInvitation} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Patient Name *
                  </label>
                  <input
                    type="text"
                    value={inviteForm.patient_name}
                    onChange={(e) => setInviteForm(prev => ({ ...prev, patient_name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="John Doe"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    value={inviteForm.email}
                    onChange={(e) => setInviteForm(prev => ({ ...prev, email: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="john@example.com"
                    required
                  />
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowInviteModal(false)}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={inviteForm.submitting}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 flex items-center"
                  >
                    {inviteForm.submitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4 mr-2" />
                        Send Invitation
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Approve Modal */}
        {showApproveModal && selectedInvitation && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl shadow-lg max-w-md w-full p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Approve Meal Plan</h2>
              <p className="text-gray-600 mb-4">For: {selectedInvitation.patient_name}</p>
              
              <form onSubmit={handleApprove} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Plan Name
                  </label>
                  <input
                    type="text"
                    value={approveForm.plan_name}
                    onChange={(e) => setApproveForm(prev => ({ ...prev, plan_name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Weekly Plan Name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes for Patient
                  </label>
                  <textarea
                    value={approveForm.notes}
                    onChange={(e) => setApproveForm(prev => ({ ...prev, notes: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Additional notes or instructions..."
                  />
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowApproveModal(false);
                      setSelectedInvitation(null);
                    }}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={approveForm.submitting}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-green-400 flex items-center"
                  >
                    {approveForm.submitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                        Approving...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Approve & Notify Patient
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
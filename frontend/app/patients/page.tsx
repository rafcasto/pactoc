'use client';

import React, { useState } from 'react';
import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { usePatients, usePatientStats, useUpdatePatientStatus, useDeletePatient, type Patient } from '@/lib/hooks/usePatients';
import { StatusBadge } from '@/components/invitations';
import { Eye, Edit, Trash2, AlertCircle, Users, UserCheck, Clock, UserX, Plus } from 'lucide-react';
import Link from 'next/link';

export default function PatientsPage() {
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  // Hooks
  const { data: patientsData, loading, error, refetch } = usePatients({
    profile_status: selectedStatus || undefined,
    search: searchTerm || undefined
  });
  const { data: statsData } = usePatientStats();
  const { updateStatus, loading: updatingStatus } = useUpdatePatientStatus();
  const { deletePatient, loading: deleting } = useDeletePatient();

  const patients = Array.isArray(patientsData?.patients) ? patientsData.patients : [];
  const stats = statsData?.stats;

  const handleUpdateStatus = async (patientId: string, status: 'pending_review' | 'approved') => {
    try {
      await updateStatus(patientId, status);
      setShowStatusModal(false);
      setSelectedPatient(null);
      refetch();
    } catch (error) {
      console.error('Failed to update patient status:', error);
    }
  };

  const handleDeletePatient = async (patientId: string) => {
    if (confirm('Are you sure you want to delete this patient? This action cannot be undone.')) {
      try {
        await deletePatient(patientId);
        refetch();
      } catch (error) {
        console.error('Failed to delete patient:', error);
      }
    }
  };



  const columns = [
    {
      key: 'name',
      title: 'Patient',
      render: (_: any, record: Patient) => (
        <div>
          <div className="font-medium text-gray-900">
            {record.first_name} {record.last_name}
          </div>
          {record.email && (
            <div className="text-sm text-gray-500">{record.email}</div>
          )}
        </div>
      )
    },
    {
      key: 'date_of_birth',
      title: 'Age',
      render: (dateOfBirth: string) => {
        const age = new Date().getFullYear() - new Date(dateOfBirth).getFullYear();
        return `${age} years`;
      }
    },
    {
      key: 'gender',
      title: 'Gender',
      render: (gender: string) => (
        <span className="capitalize">{gender}</span>
      )
    },
    {
      key: 'profile_status',
      title: 'Status',
      render: (status: string) => <StatusBadge status={status} type="patient" />
    },
    {
      key: 'conditions',
      title: 'Health Info',
      render: (_: any, record: Patient) => (
        <div className="text-sm">
          <div>Conditions: {record.conditions_count || 0}</div>
          <div>Intolerances: {record.intolerances_count || 0}</div>
          <div>Preferences: {record.preferences_count || 0}</div>
        </div>
      )
    },
    {
      key: 'created_at',
      title: 'Created',
      render: (date: string) => new Date(date).toLocaleDateString()
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (_: any, record: Patient) => (
        <div className="flex space-x-2">
          <Link href={`/patients/${record.id}`}>
            <Button size="sm" variant="ghost" title="View details">
              <Eye className="w-4 h-4" />
            </Button>
          </Link>
          <Button
            size="sm"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation();
              setSelectedPatient(record);
              setShowStatusModal(true);
            }}
            title="Update status"
          >
            <Edit className="w-4 h-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation();
              handleDeletePatient(record.id);
            }}
            loading={deleting}
            title="Delete patient"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      )
    }
  ];

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading patients</h3>
          <p className="text-gray-500 mb-4">{error}</p>
          <Button onClick={refetch}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
        <Link href="/invitations">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Invite Patient
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card className="p-4">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-blue-500 mr-3" />
              <div>
                <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
                <div className="text-sm text-gray-500">Total Patients</div>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center">
              <UserCheck className="w-8 h-8 text-green-500 mr-3" />
              <div>
                <div className="text-2xl font-bold text-green-600">{stats.active}</div>
                <div className="text-sm text-gray-500">Active</div>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-yellow-500 mr-3" />
              <div>
                <div className="text-2xl font-bold text-yellow-600">{stats.pending_review}</div>
                <div className="text-sm text-gray-500">Pending Review</div>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center">
              <UserCheck className="w-8 h-8 text-blue-500 mr-3" />
              <div>
                <div className="text-2xl font-bold text-blue-600">{stats.approved}</div>
                <div className="text-sm text-gray-500">Approved</div>
              </div>
            </div>
          </Card>
          <Card className="p-4">
            <div className="flex items-center">
              <UserX className="w-8 h-8 text-red-500 mr-3" />
              <div>
                <div className="text-2xl font-bold text-red-600">{stats.inactive}</div>
                <div className="text-sm text-gray-500">Inactive</div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Filters */}
      <div className="flex space-x-4">
        <Input
          type="text"
          placeholder="Search patients..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-xs"
        />
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm"
        >
          <option value="">All Statuses</option>
          <option value="pending_review">Pending Review</option>
          <option value="approved">Approved</option>
        </select>
      </div>

      {/* Patients Table */}
      <Card>
        <DataTable
          columns={columns}
          data={patients}
          loading={loading}
          emptyMessage="No patients found"
          onRowClick={(patient) => window.location.href = `/patients/${patient.id}`}
        />
      </Card>

      {/* Update Status Modal */}
      {showStatusModal && selectedPatient && (
        <UpdateStatusModal
          patient={selectedPatient}
          onClose={() => {
            setShowStatusModal(false);
            setSelectedPatient(null);
          }}
          onUpdate={handleUpdateStatus}
          loading={updatingStatus}
        />
      )}
      </div>
    </AuthenticatedLayout>
  );
}

interface UpdateStatusModalProps {
  patient: Patient;
  onClose: () => void;
  onUpdate: (patientId: string, status: 'pending_review' | 'approved') => void;
  loading: boolean;
}

function UpdateStatusModal({ patient, onClose, onUpdate, loading }: UpdateStatusModalProps) {
  const [newStatus, setNewStatus] = useState<'pending_review' | 'approved'>(patient.profile_status);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdate(patient.id, newStatus);
  };

  return (
    <Modal
      open={true}
      onClose={onClose}
      title="Update Patient Status"
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <p className="text-sm text-gray-600 mb-4">
            Update status for <strong>{patient.first_name} {patient.last_name}</strong>
          </p>
          
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="radio"
                name="status"
                value="pending_review"
                checked={newStatus === 'pending_review'}
                onChange={(e) => setNewStatus(e.target.value as 'pending_review')}
                className="mr-2"
              />
              <span className="text-sm">Pending Review</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="status"
                value="approved"
                checked={newStatus === 'approved'}
                onChange={(e) => setNewStatus(e.target.value as 'approved')}
                className="mr-2"
              />
              <span className="text-sm">Approved</span>
            </label>
          </div>
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            loading={loading}
            disabled={newStatus === patient.profile_status}
          >
            Update Status
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}

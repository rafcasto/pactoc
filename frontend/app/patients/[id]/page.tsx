'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { MultiSelect } from '@/components/ui/MultiSelect';
import { usePatient, useUpdatePatient, useAddPatientCondition, useRemovePatientCondition, type Patient } from '@/lib/hooks/usePatients';
import { ArrowLeft, Edit, Plus, Trash2, Calendar, Mail, Phone, AlertCircle, User, Heart, AlertTriangle, Utensils } from 'lucide-react';
import Link from 'next/link';

export default function PatientDetailPage() {
  const params = useParams();
  const patientId = params.id as string;
  
  const [showEditModal, setShowEditModal] = useState(false);
  const [showConditionsModal, setShowConditionsModal] = useState(false);

  // Hooks
  const { data: patientData, loading, error, refetch } = usePatient(patientId);
  const { updatePatient, loading: updating } = useUpdatePatient();

  const patient = patientData?.patient;

  const handleUpdatePatient = async (data: Partial<Patient>) => {
    try {
      await updatePatient(patientId, data);
      setShowEditModal(false);
      refetch();
    } catch (error) {
      console.error('Failed to update patient:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading patient</h3>
          <p className="text-gray-500 mb-4">{error || 'Patient not found'}</p>
          <Link href="/patients">
            <Button>Back to Patients</Button>
          </Link>
        </div>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-3 py-1 text-sm font-medium rounded-full";
    switch (status) {
      case 'pending_review':
        return <span className={`${baseClasses} bg-yellow-100 text-yellow-800`}>Pending Review</span>;
      case 'approved':
        return <span className={`${baseClasses} bg-green-100 text-green-800`}>Approved</span>;
      default:
        return <span className={`${baseClasses} bg-gray-100 text-gray-800`}>{status}</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link href="/patients">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Patients
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {patient.first_name} {patient.last_name}
            </h1>
            <div className="flex items-center space-x-2 mt-1">
              {getStatusBadge(patient.profile_status)}
              <span className="text-sm text-gray-500">
                Created {new Date(patient.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={() => setShowEditModal(true)}>
            <Edit className="w-4 h-4 mr-2" />
            Edit Patient
          </Button>
          <Link href={`/meal-plans/generate?patient=${patientId}`}>
            <Button>
              <Calendar className="w-4 h-4 mr-2" />
              Generate Meal Plan
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Personal Information */}
        <Card className="p-6">
          <div className="flex items-center mb-4">
            <User className="w-5 h-5 text-blue-500 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Personal Information</h3>
          </div>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">Full Name</label>
              <p className="text-gray-900">{patient.first_name} {patient.last_name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Date of Birth</label>
              <p className="text-gray-900">
                {new Date(patient.date_of_birth).toLocaleDateString()}
                <span className="text-sm text-gray-500 ml-2">
                  (Age: {new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear()})
                </span>
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Gender</label>
              <p className="text-gray-900 capitalize">{patient.gender}</p>
            </div>
            {patient.email && (
              <div>
                <label className="text-sm font-medium text-gray-500">Email</label>
                <div className="flex items-center">
                  <Mail className="w-4 h-4 text-gray-400 mr-2" />
                  <p className="text-gray-900">{patient.email}</p>
                </div>
              </div>
            )}
            {patient.phone && (
              <div>
                <label className="text-sm font-medium text-gray-500">Phone</label>
                <div className="flex items-center">
                  <Phone className="w-4 h-4 text-gray-400 mr-2" />
                  <p className="text-gray-900">{patient.phone}</p>
                </div>
              </div>
            )}
            {patient.additional_notes && (
              <div>
                <label className="text-sm font-medium text-gray-500">Additional Notes</label>
                <p className="text-gray-900 text-sm">{patient.additional_notes}</p>
              </div>
            )}
          </div>
        </Card>

        {/* Medical Conditions */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Heart className="w-5 h-5 text-red-500 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Medical Conditions</h3>
            </div>
            <Button size="sm" variant="outline" onClick={() => setShowConditionsModal(true)}>
              <Plus className="w-4 h-4" />
            </Button>
          </div>
          <div className="space-y-2">
            {patient.medical_conditions && patient.medical_conditions.length > 0 ? (
              patient.medical_conditions.map((condition) => (
                <div
                  key={condition.id}
                  className="flex items-center justify-between p-2 bg-red-50 rounded-md"
                >
                  <div>
                    <p className="text-sm font-medium text-red-800">{condition.condition_name}</p>
                    {condition.notes && (
                      <p className="text-xs text-red-600">{condition.notes}</p>
                    )}
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No medical conditions recorded</p>
            )}
          </div>
        </Card>

        {/* Food Intolerances */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-orange-500 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Food Intolerances</h3>
            </div>
            <Button size="sm" variant="outline">
              <Plus className="w-4 h-4" />
            </Button>
          </div>
          <div className="space-y-2">
            {patient.intolerances && patient.intolerances.length > 0 ? (
              patient.intolerances.map((intolerance) => (
                <div
                  key={intolerance.id}
                  className="flex items-center justify-between p-2 bg-orange-50 rounded-md"
                >
                  <div>
                    <p className="text-sm font-medium text-orange-800">{intolerance.intolerance_name}</p>
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        intolerance.severity === 'severe' ? 'bg-red-100 text-red-700' :
                        intolerance.severity === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {intolerance.severity}
                      </span>
                      {intolerance.notes && (
                        <p className="text-xs text-orange-600">{intolerance.notes}</p>
                      )}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-orange-600 hover:text-orange-800"
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No food intolerances recorded</p>
            )}
          </div>
        </Card>

        {/* Dietary Preferences */}
        <Card className="p-6 lg:col-span-3">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Utensils className="w-5 h-5 text-green-500 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Dietary Preferences</h3>
            </div>
            <Button size="sm" variant="outline">
              <Plus className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {patient.dietary_preferences && patient.dietary_preferences.length > 0 ? (
              patient.dietary_preferences.map((preference) => (
                <div
                  key={preference.id}
                  className="flex items-center space-x-2 px-3 py-1 bg-green-50 text-green-800 rounded-full text-sm"
                >
                  <span>{preference.preference_name}</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="w-4 h-4 p-0 text-green-600 hover:text-green-800"
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No dietary preferences recorded</p>
            )}
          </div>
        </Card>
      </div>

      {/* Edit Patient Modal */}
      {showEditModal && (
        <EditPatientModal
          patient={patient}
          onClose={() => setShowEditModal(false)}
          onSubmit={handleUpdatePatient}
          loading={updating}
        />
      )}
    </div>
  );
}

interface EditPatientModalProps {
  patient: Patient;
  onClose: () => void;
  onSubmit: (data: Partial<Patient>) => void;
  loading: boolean;
}

function EditPatientModal({ patient, onClose, onSubmit, loading }: EditPatientModalProps) {
  const [formData, setFormData] = useState({
    first_name: patient.first_name,
    last_name: patient.last_name,
    email: patient.email || '',
    phone: patient.phone || '',
    additional_notes: patient.additional_notes || ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Modal
      open={true}
      onClose={onClose}
      title="Edit Patient Information"
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First Name *
            </label>
            <input
              type="text"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Last Name *
            </label>
            <input
              type="text"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Phone
          </label>
          <input
            type="tel"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Additional Notes
          </label>
          <textarea
            value={formData.additional_notes}
            onChange={(e) => setFormData({ ...formData, additional_notes: e.target.value })}
            rows={3}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={loading}>
            Save Changes
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}

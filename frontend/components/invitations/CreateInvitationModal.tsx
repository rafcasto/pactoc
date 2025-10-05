'use client';

import React, { useState } from 'react';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface CreateInvitationModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: { email: string; first_name?: string; last_name?: string }) => void;
  loading: boolean;
}

export function CreateInvitationModal({ open, onClose, onSubmit, loading }: CreateInvitationModalProps) {
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('CreateInvitationModal - Form submitted');
    console.log('CreateInvitationModal - Form data:', formData);
    
    if (!formData.email) {
      console.log('CreateInvitationModal - No email provided, returning');
      return;
    }

    const submitData: any = { email: formData.email };
    if (formData.first_name) submitData.first_name = formData.first_name;
    if (formData.last_name) submitData.last_name = formData.last_name;

    console.log('CreateInvitationModal - Calling onSubmit with data:', submitData);
    onSubmit(submitData);
  };

  const resetForm = () => {
    setFormData({ email: '', first_name: '', last_name: '' });
  };

  return (
    <Modal
      open={open}
      onClose={() => {
        onClose();
        resetForm();
      }}
      title="Create Patient Invitation"
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email Address *
          </label>
          <Input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
            placeholder="patient@example.com"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First Name
            </label>
            <Input
              type="text"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              placeholder="John"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Last Name
            </label>
            <Input
              type="text"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              placeholder="Doe"
            />
          </div>
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={loading} disabled={!formData.email}>
            Create Invitation
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}

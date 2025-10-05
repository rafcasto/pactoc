'use client';

import { useState } from 'react';

export function useInvitationActions({
  onResend,
  onRegenerate,
  onCancel,
  onRefetch
}: {
  onResend?: (id: string) => Promise<void>;
  onRegenerate?: (id: string) => Promise<void>;
  onCancel?: (id: string) => Promise<void>;
  onRefetch?: () => void;
}) {
  const [copiedLink, setCopiedLink] = useState<string | null>(null);

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedLink(text);
      setTimeout(() => setCopiedLink(null), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const handleResendInvitation = async (invitationId: string) => {
    try {
      if (onResend) {
        await onResend(invitationId);
        onRefetch?.();
      }
    } catch (error) {
      console.error('Failed to resend invitation:', error);
    }
  };

  const handleRegenerateInvitation = async (invitationId: string) => {
    if (confirm('Are you sure you want to regenerate this invitation link? The old link will no longer work.')) {
      try {
        if (onRegenerate) {
          await onRegenerate(invitationId);
          onRefetch?.();
        }
      } catch (error) {
        console.error('Failed to regenerate invitation:', error);
      }
    }
  };

  const handleCancelInvitation = async (invitationId: string) => {
    if (confirm('Are you sure you want to cancel this invitation?')) {
      try {
        if (onCancel) {
          await onCancel(invitationId);
          onRefetch?.();
        }
      } catch (error) {
        console.error('Failed to cancel invitation:', error);
      }
    }
  };

  return {
    copiedLink,
    copyToClipboard,
    handleResendInvitation,
    handleRegenerateInvitation,
    handleCancelInvitation
  };
}

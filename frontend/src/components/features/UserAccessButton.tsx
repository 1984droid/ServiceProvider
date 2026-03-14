/**
 * UserAccessButton - Generic component for granting/revoking user access
 *
 * Works for both Employee and Contact (customer portal access)
 */

import { useState } from 'react';

interface UserAccessButtonProps {
  personType: 'employee' | 'contact';
  personName: string;
  personId: string;
  emailOrIdentifier?: string;
  hasAccess: boolean;
  username?: string;
  onGrantAccess: () => Promise<{ temporary_password?: string }>;
  onRevokeAccess: () => Promise<void>;
  onSuccess: () => void;
}

export function UserAccessButton({
  personType,
  personName,
  personId,
  emailOrIdentifier,
  hasAccess,
  username,
  onGrantAccess,
  onRevokeAccess,
  onSuccess,
}: UserAccessButtonProps) {
  const [showModal, setShowModal] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tempPassword, setTempPassword] = useState<string | null>(null);

  const handleGrant = async () => {
    setIsProcessing(true);
    setError(null);
    setTempPassword(null);

    try {
      const result = await onGrantAccess();
      setTempPassword(result.temporary_password || null);

      // Auto-close after delay if no password to show
      if (!result.temporary_password) {
        setTimeout(() => {
          setShowModal(false);
          onSuccess();
        }, 2000);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to grant access');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRevoke = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      await onRevokeAccess();
      setShowModal(false);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to revoke access');
    } finally {
      setIsProcessing(false);
    }
  };

  const accessLabel = personType === 'employee' ? 'Portal Access' : 'Customer Portal Access';

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="text-xs font-medium hover:underline"
        style={{ color: hasAccess ? '#dc2626' : '#7ed321' }}
      >
        {hasAccess ? 'Revoke' : 'Grant Access'}
      </button>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-900">
              {hasAccess ? `Revoke ${accessLabel}` : `Grant ${accessLabel}`}
            </h3>

            {/* Success - Show temp password */}
            {tempPassword && (
              <div className="mb-4">
                <div className="p-4 rounded-lg bg-green-50 border-2 border-green-600">
                  <p className="text-sm font-semibold mb-2 text-green-900">
                    ✓ Access Granted!
                  </p>
                  <p className="text-sm mb-2 text-green-900">
                    Username: <strong>{emailOrIdentifier?.split('@')[0] || personId}</strong>
                  </p>
                  <p className="text-sm mb-2 text-green-900">
                    Temporary Password:
                  </p>
                  <div className="p-2 rounded font-mono text-sm bg-white border border-green-600">
                    {tempPassword}
                  </div>
                  <p className="text-xs mt-2 text-green-900">
                    ⚠️ Save this password now - it will not be shown again!
                  </p>
                </div>
                <div className="mt-4 flex justify-end">
                  <button
                    onClick={() => {
                      setShowModal(false);
                      onSuccess();
                    }}
                    className="px-4 py-2 text-sm font-medium text-white rounded"
                    style={{ backgroundColor: '#7ed321' }}
                  >
                    Done
                  </button>
                </div>
              </div>
            )}

            {/* Grant Access Confirmation */}
            {!hasAccess && !tempPassword && (
              <>
                <p className="text-sm mb-4 text-gray-600">
                  Create a user account for <strong>{personName}</strong>?
                </p>
                <p className="text-sm mb-4 text-gray-600">
                  A username and temporary password will be generated automatically.
                </p>

                {error && (
                  <div className="mb-4 p-3 rounded text-sm bg-red-50 text-red-900">
                    {error}
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowModal(false)}
                    disabled={isProcessing}
                    className="flex-1 px-4 py-2 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleGrant}
                    disabled={isProcessing}
                    className="flex-1 px-4 py-2 text-sm font-medium text-white rounded disabled:opacity-50"
                    style={{ backgroundColor: '#7ed321' }}
                  >
                    {isProcessing ? 'Creating...' : 'Grant Access'}
                  </button>
                </div>
              </>
            )}

            {/* Revoke Access Confirmation */}
            {hasAccess && !tempPassword && (
              <>
                <p className="text-sm mb-4 text-gray-600">
                  Revoke {accessLabel.toLowerCase()} for <strong>{personName}</strong>?
                </p>
                <p className="text-sm mb-4 text-gray-600">
                  Username: <strong>{username}</strong>
                </p>
                <p className="text-sm mb-4 text-red-700">
                  The user account will be deactivated and unlinked. The {personType} record will remain.
                </p>

                {error && (
                  <div className="mb-4 p-3 rounded text-sm bg-red-50 text-red-900">
                    {error}
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowModal(false)}
                    disabled={isProcessing}
                    className="flex-1 px-4 py-2 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleRevoke}
                    disabled={isProcessing}
                    className="flex-1 px-4 py-2 text-sm font-medium text-white rounded disabled:opacity-50"
                    style={{ backgroundColor: '#dc2626' }}
                  >
                    {isProcessing ? 'Revoking...' : 'Revoke Access'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}

/**
 * ContactUserAccessButton
 *
 * Grant or revoke customer portal access for a contact (wrapper around generic UserAccessButton)
 */

import { contactsApi, type Contact } from '@/api/contacts.api';
import { UserAccessButton } from '@/components/features/UserAccessButton';

interface ContactUserAccessButtonProps {
  contact: Contact;
  onSuccess: () => void;
}

export function ContactUserAccessButton({
  contact,
  onSuccess,
}: ContactUserAccessButtonProps) {
  return (
    <UserAccessButton
      personType="contact"
      personName={contact.full_name}
      personId={contact.id}
      emailOrIdentifier={contact.email}
      hasAccess={contact.has_user_account}
      username={contact.user_info?.username}
      onGrantAccess={() => contactsApi.createUser(contact.id)}
      onRevokeAccess={() => contactsApi.revokeUser(contact.id, false)}
      onSuccess={onSuccess}
    />
  );
}

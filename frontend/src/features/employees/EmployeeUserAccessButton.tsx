/**
 * EmployeeUserAccessButton
 *
 * Grant or revoke user access for an employee (wrapper around generic UserAccessButton)
 */

import { employeesApi, type Employee } from '@/api/employees.api';
import { UserAccessButton } from '@/components/features/UserAccessButton';

interface EmployeeUserAccessButtonProps {
  employee: Employee;
  onSuccess: () => void;
}

export function EmployeeUserAccessButton({
  employee,
  onSuccess,
}: EmployeeUserAccessButtonProps) {
  return (
    <UserAccessButton
      personType="employee"
      personName={employee.full_name}
      personId={employee.employee_number}
      emailOrIdentifier={employee.email}
      hasAccess={employee.has_user_account}
      username={employee.user_info?.username}
      onGrantAccess={() => employeesApi.createUser(employee.id)}
      onRevokeAccess={() => employeesApi.revokeUser(employee.id, false)}
      onSuccess={onSuccess}
    />
  );
}

/**
 * Validation Utilities for Inspection Fields
 */

interface TemplateField {
  field_id: string;
  type: string;
  label: string;
  required?: boolean;
  min?: number;
  max?: number;
  precision?: number;
  values?: string[];
  conditionally_required_if?: {
    any_field_in?: string[];
    description?: string;
  };
  conditionally_suggested_if?: {
    any_field_in?: string[];
    description?: string;
  };
}

interface ValidationError {
  field_id: string;
  message: string;
}

/**
 * Validate a single field value
 */
export function validateField(
  field: TemplateField,
  value: any,
  allValues?: Record<string, any>
): string | null {
  const fieldType = field.type.toUpperCase();

  // Check required
  if (field.required) {
    if (value === null || value === undefined) {
      return `${field.label} is required`;
    }

    if (typeof value === 'string' && value.trim() === '') {
      return `${field.label} is required`;
    }

    if (Array.isArray(value) && value.length === 0) {
      return `${field.label} is required`;
    }
  }

  // Check conditional requirements (e.g., photo required when defect found)
  if (field.conditionally_required_if && allValues) {
    const condition = field.conditionally_required_if;

    if (condition.any_field_in) {
      const triggerValues = condition.any_field_in;
      const hasTriggeringValue = Object.values(allValues).some(v =>
        triggerValues.includes(v)
      );

      if (hasTriggeringValue) {
        // This field is now required
        if (value === null || value === undefined) {
          return `${field.label} is required when defects are found`;
        }

        if (typeof value === 'string' && value.trim() === '') {
          return `${field.label} is required when defects are found`;
        }

        if (Array.isArray(value) && value.length === 0) {
          return `${field.label} is required when defects are found`;
        }
      }
    }
  }

  // If value is empty and not required, skip further validation
  if (value === null || value === undefined || value === '') {
    return null;
  }

  // Type-specific validation
  switch (fieldType) {
    case 'NUMBER':
      return validateNumber(field, value);

    case 'TEXT':
    case 'TEXT_AREA':
    case 'TEXTAREA':
      return validateText(field, value);

    case 'ENUM':
      return validateEnum(field, value);

    case 'CHOICE_MULTI':
      return validateChoiceMulti(field, value);

    case 'BOOLEAN':
      return validateBoolean(field, value);

    case 'PHOTO':
    case 'ATTACHMENTS':
      return validatePhoto(field, value);

    default:
      return null;
  }
}

function validateNumber(field: TemplateField, value: any): string | null {
  const num = Number(value);

  if (isNaN(num)) {
    return `${field.label} must be a valid number`;
  }

  if (field.min != null && num < field.min) {
    return `${field.label} must be at least ${field.min}`;
  }

  if (field.max != null && num > field.max) {
    return `${field.label} must be at most ${field.max}`;
  }

  // Check precision
  if (field.precision != null) {
    const decimalPlaces = (value.toString().split('.')[1] || '').length;
    if (decimalPlaces > field.precision) {
      return `${field.label} can have at most ${field.precision} decimal places`;
    }
  }

  return null;
}

function validateText(field: TemplateField, value: any): string | null {
  if (typeof value !== 'string') {
    return `${field.label} must be text`;
  }

  // Could add min/max length if needed
  if (field.min != null && value.length < field.min) {
    return `${field.label} must be at least ${field.min} characters`;
  }

  if (field.max != null && value.length > field.max) {
    return `${field.label} must be at most ${field.max} characters`;
  }

  return null;
}

function validateEnum(field: TemplateField, value: any): string | null {
  if (typeof value !== 'string') {
    return `${field.label} must be a valid selection`;
  }

  if (field.values && !field.values.includes(value)) {
    return `${field.label} must be one of the provided options`;
  }

  return null;
}

function validateChoiceMulti(field: TemplateField, value: any): string | null {
  if (!Array.isArray(value)) {
    return `${field.label} must be a list of selections`;
  }

  if (field.values) {
    for (const item of value) {
      if (!field.values.includes(item)) {
        return `${field.label} contains invalid option: ${item}`;
      }
    }
  }

  return null;
}

function validateBoolean(field: TemplateField, value: any): string | null {
  if (typeof value !== 'boolean') {
    return `${field.label} must be true or false`;
  }

  return null;
}

function validatePhoto(field: TemplateField, value: any): string | null {
  if (!Array.isArray(value)) {
    return `${field.label} must be a list of photos`;
  }

  // Could add max photos validation if needed
  if (field.max !== undefined && value.length > field.max) {
    return `${field.label} can have at most ${field.max} photos`;
  }

  return null;
}

/**
 * Validate all fields in a step
 */
export function validateStep(
  fields: TemplateField[],
  values: Record<string, any>,
  enumValues: Record<string, string[]> = {}
): Record<string, string> {
  const errors: Record<string, string> = {};

  for (const field of fields) {
    // Resolve enum values if needed
    let fieldToValidate = field;
    if (field.type.toUpperCase() === 'ENUM' && field.enum_ref && !field.values) {
      fieldToValidate = {
        ...field,
        values: enumValues[field.enum_ref] || [],
      };
    }

    const value = values[field.field_id];
    const error = validateField(fieldToValidate, value, values);

    if (error) {
      errors[field.field_id] = error;
    }
  }

  return errors;
}

/**
 * Check if step is valid (no errors)
 */
export function isStepValid(
  fields: TemplateField[],
  values: Record<string, any>,
  enumValues: Record<string, string[]> = {}
): boolean {
  const errors = validateStep(fields, values, enumValues);
  return Object.keys(errors).length === 0;
}

/**
 * Get warnings for fields (non-blocking suggestions)
 */
export function getStepWarnings(
  fields: TemplateField[],
  values: Record<string, any>
): Record<string, string> {
  const warnings: Record<string, string> = {};

  for (const field of fields) {
    // Check conditional suggestions (e.g., photo suggested for minor issues)
    if (field.conditionally_suggested_if) {
      const condition = field.conditionally_suggested_if;

      if (condition.any_field_in) {
        const triggerValues = condition.any_field_in;
        const hasTriggeringValue = Object.values(values).some(v =>
          triggerValues.includes(v)
        );

        if (hasTriggeringValue) {
          const value = values[field.field_id];

          // Check if field is empty
          const isEmpty =
            value === null ||
            value === undefined ||
            (typeof value === 'string' && value.trim() === '') ||
            (Array.isArray(value) && value.length === 0);

          if (isEmpty) {
            warnings[field.field_id] =
              condition.description || `${field.label} is strongly recommended`;
          }
        }
      }
    }
  }

  return warnings;
}

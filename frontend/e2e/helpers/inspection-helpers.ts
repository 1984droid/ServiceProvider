/**
 * Inspection Helper Functions
 *
 * Reusable functions for common inspection operations
 */

import { Page } from '@playwright/test';
import { apiClient } from '../../src/lib/axios';

export interface InspectionStepData {
  step_id: string;
  fields: Record<string, any>;
}

/**
 * Fill out an entire inspection programmatically via API
 */
export async function fillInspectionViaAPI(
  inspectionId: string,
  stepData: InspectionStepData[]
): Promise<void> {
  for (const step of stepData) {
    await apiClient.post(`/inspections/${inspectionId}/save_step/`, {
      step_id: step.step_id,
      data: step.fields,
    });
  }
}

/**
 * Complete an inspection and finalize it
 */
export async function completeAndFinalizeInspection(
  inspectionId: string,
  signatureData?: string
): Promise<void> {
  await apiClient.post(`/inspections/${inspectionId}/finalize/`, {
    signature_data: signatureData || null,
    force: false,
  });
}

/**
 * Navigate through inspection steps in UI
 */
export async function navigateInspectionSteps(
  page: Page,
  stepCount: number
): Promise<void> {
  for (let i = 0; i < stepCount - 1; i++) {
    const nextButton = page.getByRole('button', { name: /next/i });
    if (await nextButton.isVisible()) {
      await nextButton.click();
      await page.waitForTimeout(500);
    }
  }
}

/**
 * Fill a text field in current inspection step
 */
export async function fillInspectionTextField(
  page: Page,
  fieldLabel: string,
  value: string
): Promise<void> {
  const field = page.getByLabel(new RegExp(fieldLabel, 'i'));
  await field.fill(value);
}

/**
 * Select a dropdown value in current inspection step
 */
export async function selectInspectionDropdown(
  page: Page,
  fieldLabel: string,
  value: string
): Promise<void> {
  const field = page.getByLabel(new RegExp(fieldLabel, 'i'));
  await field.selectOption(value);
}

/**
 * Check a checkbox in current inspection step
 */
export async function checkInspectionCheckbox(
  page: Page,
  fieldLabel: string
): Promise<void> {
  const field = page.getByLabel(new RegExp(fieldLabel, 'i'));
  await field.check();
}

/**
 * Add a defect during inspection
 */
export async function addDefectViaUI(
  page: Page,
  description: string,
  severity: 'ADVISORY' | 'MINOR' | 'MAJOR' | 'CRITICAL'
): Promise<void> {
  // Click add defect button
  const addDefectButton = page.getByRole('button', { name: /add defect/i });
  await addDefectButton.click();
  await page.waitForTimeout(300);

  // Fill defect form
  const descField = page.locator('#defect-description, [name="description"]').first();
  await descField.fill(description);

  const severityField = page.locator('#defect-severity, [name="severity"]').first();
  await severityField.selectOption(severity);

  // Save defect
  const saveButton = page.getByRole('button', { name: /save|add/i }).last();
  await saveButton.click();
  await page.waitForTimeout(500);
}

/**
 * Add a defect via API
 */
export async function addDefectViaAPI(
  inspectionId: string,
  defectData: {
    step_id: string;
    field_id: string;
    severity: 'ADVISORY' | 'MINOR' | 'MAJOR' | 'CRITICAL';
    description: string;
    location?: string;
  }
): Promise<string> {
  const response = await apiClient.post(`/inspections/${inspectionId}/defects/`, defectData);
  return response.data.id;
}

/**
 * Create a complete inspection with all steps filled
 */
export async function createCompleteInspection(
  customerId: string,
  assetType: 'VEHICLE' | 'EQUIPMENT',
  assetId: string,
  templateKey: string
): Promise<string> {
  // Create inspection
  const createResponse = await apiClient.post('/inspections/', {
    template_key: templateKey,
    asset_type: assetType,
    asset_id: assetId,
    inspector_name: 'Test Inspector',
  });

  const inspectionId = createResponse.data.id;

  // Get template to know which steps to fill
  const templateResponse = await apiClient.get(`/templates/${templateKey}/`);
  const steps = templateResponse.data.procedure?.steps || [];

  // Fill all required fields with dummy data
  for (const step of steps) {
    const stepData: Record<string, any> = {};

    for (const field of step.fields || []) {
      if (field.required) {
        // Fill with appropriate dummy data based on field type
        switch (field.type) {
          case 'text':
            stepData[field.field_id] = 'Test value';
            break;
          case 'number':
            stepData[field.field_id] = 100;
            break;
          case 'boolean':
            stepData[field.field_id] = true;
            break;
          case 'select':
          case 'radio':
            if (field.values && field.values.length > 0) {
              stepData[field.field_id] = field.values[0];
            }
            break;
          case 'checkbox':
            if (field.values && field.values.length > 0) {
              stepData[field.field_id] = [field.values[0]];
            }
            break;
          case 'date':
            stepData[field.field_id] = new Date().toISOString().split('T')[0];
            break;
        }
      }
    }

    // Save step data
    if (Object.keys(stepData).length > 0) {
      await apiClient.post(`/inspections/${inspectionId}/save_step/`, {
        step_id: step.step_id,
        data: stepData,
      });
    }
  }

  return inspectionId;
}

/**
 * Wait for inspection to be ready to finalize
 */
export async function waitForInspectionReady(
  inspectionId: string,
  maxAttempts: number = 10
): Promise<boolean> {
  for (let i = 0; i < maxAttempts; i++) {
    const response = await apiClient.get(`/inspections/${inspectionId}/`);
    const completion = response.data.completion_status;

    if (completion?.is_ready_to_finalize) {
      return true;
    }

    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  return false;
}

/**
 * Upload a photo to an inspection step
 */
export async function uploadInspectionPhoto(
  inspectionId: string,
  stepKey: string,
  imageBlob: Blob,
  caption?: string
): Promise<string> {
  const formData = new FormData();
  formData.append('image', imageBlob, 'test-photo.jpg');
  formData.append('step_key', stepKey);

  if (caption) {
    formData.append('caption', caption);
  }

  const response = await apiClient.post(
    `/inspections/${inspectionId}/upload_photo/`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data.id;
}

/**
 * Get inspection completion percentage
 */
export async function getInspectionCompletion(inspectionId: string): Promise<number> {
  const response = await apiClient.get(`/inspections/${inspectionId}/`);
  return response.data.completion_status?.percent_complete || 0;
}

/**
 * Get inspection defect count
 */
export async function getInspectionDefectCount(inspectionId: string): Promise<number> {
  const response = await apiClient.get(`/inspections/${inspectionId}/`);
  return response.data.defect_count || 0;
}

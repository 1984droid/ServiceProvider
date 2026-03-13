/**
 * CreateInspectionModal - Modal for creating a new inspection
 *
 * Allows user to select an inspection template and create a new inspection run.
 * Pre-filled with asset information from the calling context.
 */

import { useState, useEffect } from 'react';
import { inspectionsApi } from '@/api/inspections.api';
import type { InspectionTemplate } from '@/api/inspections.api';

interface CreateInspectionModalProps {
  assetType: 'VEHICLE' | 'EQUIPMENT';
  assetId: string;
  assetName: string; // For display (e.g., "Unit MID-001" or "Asset MID-E001")
  equipmentType?: string; // For filtering templates
  onClose: () => void;
  onSuccess: (inspectionId: string) => void;
}

export function CreateInspectionModal({
  assetType,
  assetId,
  assetName,
  equipmentType,
  onClose,
  onSuccess,
}: CreateInspectionModalProps) {
  const [templates, setTemplates] = useState<InspectionTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [inspectorName, setInspectorName] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTemplates();
  }, [assetType, equipmentType]);

  const loadTemplates = async () => {
    setLoading(true);
    setError(null);
    try {
      let response;
      if (assetType === 'EQUIPMENT' && equipmentType) {
        response = await inspectionsApi.getTemplatesForEquipment(equipmentType);
      } else {
        response = await inspectionsApi.listTemplates();
      }

      // Filter published templates only
      const publishedTemplates = response.templates.filter(t => t.published);
      setTemplates(publishedTemplates);

      // Auto-select if only one template
      if (publishedTemplates.length === 1) {
        setSelectedTemplate(publishedTemplates[0].key);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load inspection templates');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!selectedTemplate) {
      setError('Please select an inspection template');
      return;
    }

    setCreating(true);
    setError(null);

    try {
      const inspection = await inspectionsApi.create({
        template_key: selectedTemplate,
        asset_type: assetType,
        asset_id: assetId,
        inspector_name: inspectorName || undefined,
      });

      onSuccess(inspection.id);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to create inspection');
      setCreating(false);
    }
  };

  const selectedTemplateInfo = templates.find(t => t.key === selectedTemplate);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Create Inspection</h2>
            <p className="text-sm text-gray-600 mt-0.5">{assetName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded transition-colors"
            disabled={creating}
          >
            <svg className="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mb-2" />
              <p className="text-sm text-gray-600">Loading templates...</p>
            </div>
          )}

          {error && (
            <div className="border border-red-200 rounded-lg p-4 bg-red-50 mb-4">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
          )}

          {!loading && templates.length === 0 && (
            <div className="text-center py-8">
              <svg className="w-16 h-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-4 text-lg font-semibold text-gray-900">No Templates Available</h3>
              <p className="mt-2 text-sm text-gray-500">
                No inspection templates are available for this asset type.
              </p>
            </div>
          )}

          {!loading && templates.length > 0 && (
            <div className="space-y-4">
              {/* Inspector Name */}
              <div>
                <label htmlFor="inspector_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Inspector Name (Optional)
                </label>
                <input
                  type="text"
                  id="inspector_name"
                  value={inspectorName}
                  onChange={(e) => setInspectorName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-0"
                  placeholder="Enter inspector name"
                />
              </div>

              {/* Template Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Inspection Template <span className="text-red-500">*</span>
                </label>
                <div className="space-y-2">
                  {templates.map((template) => (
                    <button
                      key={template.key}
                      onClick={() => setSelectedTemplate(template.key)}
                      className={`w-full text-left border rounded-lg p-4 transition-all ${
                        selectedTemplate === template.key
                          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">{template.name}</h4>
                          <p className="text-xs text-gray-500 mt-0.5">Version {template.version}</p>
                          {template.description && (
                            <p className="text-sm text-gray-600 mt-2">{template.description}</p>
                          )}
                          {template.standard_reference && (
                            <p className="text-xs text-gray-500 mt-1">Standard: {template.standard_reference}</p>
                          )}
                        </div>
                        {selectedTemplate === template.key && (
                          <svg className="w-6 h-6 text-blue-600 flex-shrink-0 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Template Info */}
              {selectedTemplateInfo && (
                <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                  <h5 className="text-sm font-semibold text-blue-900 mb-2">Selected Template</h5>
                  <dl className="text-sm space-y-1">
                    <div>
                      <dt className="inline font-medium text-blue-800">Name:</dt>
                      <dd className="inline ml-2 text-blue-900">{selectedTemplateInfo.name}</dd>
                    </div>
                    <div>
                      <dt className="inline font-medium text-blue-800">Version:</dt>
                      <dd className="inline ml-2 text-blue-900">{selectedTemplateInfo.version}</dd>
                    </div>
                    {selectedTemplateInfo.standard_reference && (
                      <div>
                        <dt className="inline font-medium text-blue-800">Standard:</dt>
                        <dd className="inline ml-2 text-blue-900">{selectedTemplateInfo.standard_reference}</dd>
                      </div>
                    )}
                  </dl>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        {!loading && templates.length > 0 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-end gap-3">
            <button
              onClick={onClose}
              disabled={creating}
              className="px-6 py-2.5 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={creating || !selectedTemplate}
              className="px-6 py-2.5 text-sm font-medium text-white rounded transition-colors disabled:opacity-50"
              style={{ backgroundColor: '#7ed321' }}
            >
              {creating ? 'Creating...' : 'Create Inspection'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

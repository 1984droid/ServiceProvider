/**
 * WorkOrderCreatePage
 *
 * Form for creating new work orders with cascading dropdowns
 * Includes customer selection → asset type → asset → work order details → work order lines
 */

import { useState, useEffect } from 'react';
import { customersApi, type Customer } from '@/api/customers.api';
import { workOrdersApi, type Asset, type CreateWorkOrderData } from '@/api/workOrders.api';
import { vocabularyApi } from '@/api/vocabulary.api';

interface WorkOrderLine {
  verb: string;
  noun: string;
  service_location: string;
  description: string;
  estimated_hours: number | '';
}

interface WorkOrderCreatePageProps {
  onCancel: () => void;
  onSuccess: (workOrderId: string) => void;
}

export function WorkOrderCreatePage({ onCancel, onSuccess }: WorkOrderCreatePageProps) {
  // Form state
  const [customer, setCustomer] = useState('');
  const [assetType, setAssetType] = useState<'VEHICLE' | 'EQUIPMENT' | ''>('');
  const [assetId, setAssetId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'LOW' | 'NORMAL' | 'HIGH' | 'EMERGENCY'>('NORMAL');
  const [sourceType, setSourceType] = useState<'MANUAL'>('MANUAL');
  const [lines, setLines] = useState<WorkOrderLine[]>([]);

  // Data state
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [verbs, setVerbs] = useState<string[]>([]);
  const [nouns, setNouns] = useState<string[]>([]);
  const [serviceLocations, setServiceLocations] = useState<string[]>([]);

  // Loading and error state
  const [isLoadingCustomers, setIsLoadingCustomers] = useState(true);
  const [isLoadingAssets, setIsLoadingAssets] = useState(false);
  const [isLoadingVocabulary, setIsLoadingVocabulary] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load customers on mount
  useEffect(() => {
    loadCustomers();
    loadVocabulary();
  }, []);

  // Load assets when customer and asset type change
  useEffect(() => {
    if (customer && assetType) {
      loadAssets();
    } else {
      setAssets([]);
      setAssetId('');
    }
  }, [customer, assetType]);

  const loadCustomers = async () => {
    setIsLoadingCustomers(true);
    try {
      const data = await customersApi.list();
      setCustomers(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load customers');
    } finally {
      setIsLoadingCustomers(false);
    }
  };

  const loadAssets = async () => {
    if (!customer || !assetType) return;

    setIsLoadingAssets(true);
    try {
      const data = await workOrdersApi.getAvailableAssets(customer, assetType);
      setAssets(data.assets || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load assets');
    } finally {
      setIsLoadingAssets(false);
    }
  };

  const loadVocabulary = async () => {
    setIsLoadingVocabulary(true);
    try {
      const [verbsData, nounsData, locationsData] = await Promise.all([
        vocabularyApi.getVerbs(),
        vocabularyApi.getNouns(),
        vocabularyApi.getServiceLocations(),
      ]);
      setVerbs(verbsData.verbs || []);
      setNouns(nounsData.nouns || []);
      setServiceLocations(locationsData.service_locations || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load vocabulary');
    } finally {
      setIsLoadingVocabulary(false);
    }
  };

  const addLine = () => {
    setLines([
      ...lines,
      {
        verb: '',
        noun: '',
        service_location: '',
        description: '',
        estimated_hours: '',
      },
    ]);
  };

  const removeLine = (index: number) => {
    setLines(lines.filter((_, i) => i !== index));
  };

  const updateLine = (index: number, field: keyof WorkOrderLine, value: string | number) => {
    const newLines = [...lines];
    newLines[index] = { ...newLines[index], [field]: value };
    setLines(newLines);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!customer) {
      setError('Please select a customer');
      return;
    }
    if (!assetType) {
      setError('Please select an asset type');
      return;
    }
    if (!assetId) {
      setError('Please select an asset');
      return;
    }
    if (!title.trim()) {
      setError('Please enter a title');
      return;
    }
    if (!description.trim()) {
      setError('Please enter a description');
      return;
    }
    if (lines.length === 0) {
      setError('Please add at least one work order line');
      return;
    }

    // Validate all lines have verb and noun
    for (let i = 0; i < lines.length; i++) {
      if (!lines[i].verb || !lines[i].noun) {
        setError(`Line ${i + 1}: Verb and Noun are required`);
        return;
      }
    }

    setIsSaving(true);

    try {
      const data: CreateWorkOrderData = {
        customer,
        asset_type: assetType,
        asset_id: assetId,
        title,
        description,
        priority,
        source_type: sourceType,
        lines: lines.map((line) => ({
          verb: line.verb,
          noun: line.noun,
          service_location: line.service_location || undefined,
          description: line.description || undefined,
          estimated_hours: line.estimated_hours ? Number(line.estimated_hours) : undefined,
        })),
      };

      const workOrder = await workOrdersApi.create(data);
      onSuccess(workOrder.id);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to create work order');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-2xl font-bold text-gray-900">Create Work Order</h1>
          <p className="text-sm text-gray-600 mt-1">Fill in the details to create a new work order</p>
        </div>
      </div>

      {/* Form */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4">
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          {/* Asset Selection */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Asset Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Customer */}
              <div>
                <label htmlFor="customer" className="block text-sm font-medium text-gray-700 mb-2">
                  Customer *
                </label>
                <select
                  id="customer"
                  value={customer}
                  onChange={(e) => setCustomer(e.target.value)}
                  disabled={isLoadingCustomers}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select Customer</option>
                  {customers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Asset Type */}
              <div>
                <label htmlFor="asset-type" className="block text-sm font-medium text-gray-700 mb-2">
                  Asset Type *
                </label>
                <select
                  id="asset-type"
                  value={assetType}
                  onChange={(e) => setAssetType(e.target.value as 'VEHICLE' | 'EQUIPMENT')}
                  disabled={!customer}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select Asset Type</option>
                  <option value="VEHICLE">Vehicle</option>
                  <option value="EQUIPMENT">Equipment</option>
                </select>
              </div>

              {/* Asset */}
              <div>
                <label htmlFor="asset" className="block text-sm font-medium text-gray-700 mb-2">
                  Asset *
                </label>
                <select
                  id="asset"
                  value={assetId}
                  onChange={(e) => setAssetId(e.target.value)}
                  disabled={!customer || !assetType || isLoadingAssets}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">
                    {isLoadingAssets
                      ? 'Loading assets...'
                      : assets.length === 0
                      ? 'No assets available'
                      : 'Select Asset'}
                  </option>
                  {assets.map((asset) => (
                    <option key={asset.id} value={asset.id}>
                      {asset.display_name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Work Order Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Work Order Details</h2>
            <div className="space-y-4">
              {/* Title */}
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                  Title *
                </label>
                <input
                  id="title"
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Brief title for the work order"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              {/* Description */}
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                  Description *
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Detailed description of the work to be performed"
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>

              {/* Priority and Source Type */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
                    Priority *
                  </label>
                  <select
                    id="priority"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as typeof priority)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  >
                    <option value="LOW">Low</option>
                    <option value="NORMAL">Normal</option>
                    <option value="HIGH">High</option>
                    <option value="EMERGENCY">Emergency</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="source" className="block text-sm font-medium text-gray-700 mb-2">
                    Source *
                  </label>
                  <select
                    id="source"
                    value={sourceType}
                    onChange={(e) => setSourceType(e.target.value as typeof sourceType)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  >
                    <option value="MANUAL">Manual</option>
                    <option value="CUSTOMER_REQUEST">Customer Request</option>
                    <option value="BREAKDOWN">Breakdown</option>
                    <option value="MAINTENANCE_SCHEDULE">Maintenance Schedule</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Work Order Lines */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Work Items</h2>
              <button
                type="button"
                onClick={addLine}
                disabled={isLoadingVocabulary}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Line
              </button>
            </div>

            {lines.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">
                No work items added yet. Click "Add Line" to add work items.
              </p>
            ) : (
              <div className="space-y-4">
                {lines.map((line, index) => (
                  <div
                    key={index}
                    data-testid="work-line"
                    className="p-4 border border-gray-200 rounded-lg relative"
                  >
                    <button
                      type="button"
                      onClick={() => removeLine(index)}
                      className="absolute top-2 right-2 p-1 text-red-600 hover:bg-red-50 rounded"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Verb */}
                      <div>
                        <label htmlFor={`verb-${index}`} className="block text-sm font-medium text-gray-700 mb-2">
                          Verb *
                        </label>
                        <select
                          id={`verb-${index}`}
                          value={line.verb}
                          onChange={(e) => updateLine(index, 'verb', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          required
                        >
                          <option value="">Select Verb</option>
                          {verbs.map((verb) => (
                            <option key={verb} value={verb}>
                              {verb}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Noun */}
                      <div>
                        <label htmlFor={`noun-${index}`} className="block text-sm font-medium text-gray-700 mb-2">
                          Noun *
                        </label>
                        <select
                          id={`noun-${index}`}
                          value={line.noun}
                          onChange={(e) => updateLine(index, 'noun', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          required
                        >
                          <option value="">Select Noun</option>
                          {nouns.map((noun) => (
                            <option key={noun} value={noun}>
                              {noun}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Location */}
                      <div>
                        <label htmlFor={`location-${index}`} className="block text-sm font-medium text-gray-700 mb-2">
                          Location
                        </label>
                        <select
                          id={`location-${index}`}
                          value={line.service_location}
                          onChange={(e) => updateLine(index, 'service_location', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="">Select Location</option>
                          {serviceLocations.map((loc) => (
                            <option key={loc} value={loc}>
                              {loc}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Estimated Hours */}
                      <div>
                        <label htmlFor={`hours-${index}`} className="block text-sm font-medium text-gray-700 mb-2">
                          Estimated Hours
                        </label>
                        <input
                          id={`hours-${index}`}
                          type="number"
                          step="0.5"
                          min="0"
                          value={line.estimated_hours}
                          onChange={(e) => updateLine(index, 'estimated_hours', e.target.value)}
                          placeholder="0.0"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>

                      {/* Line Description */}
                      <div className="md:col-span-2">
                        <label htmlFor={`line-desc-${index}`} className="block text-sm font-medium text-gray-700 mb-2">
                          Additional Details
                        </label>
                        <input
                          id={`line-desc-${index}`}
                          type="text"
                          value={line.description}
                          onChange={(e) => updateLine(index, 'description', e.target.value)}
                          placeholder="Optional additional details for this work item"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onCancel}
              disabled={isSaving}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? 'Creating...' : 'Create Work Order'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/**
 * VehicleVINDecodeTab - VIN decode information and decode action
 */

import { useState } from 'react';
import type { Vehicle } from '@/api/assets.api';

interface VehicleVINDecodeTabProps {
  vehicle: Vehicle;
  onVINDecoded: () => void;
}

export function VehicleVINDecodeTab({ vehicle, onVINDecoded }: VehicleVINDecodeTabProps) {
  const [isDecoding, setIsDecoding] = useState(false);
  const [decodeError, setDecodeError] = useState<string | null>(null);

  const vinDecodeData = vehicle.vin_decode_data;

  const handleDecode = async () => {
    setIsDecoding(true);
    setDecodeError(null);

    try {
      // VIN decode API integration not implemented
      setDecodeError('VIN decode API integration coming soon');

      // onVINDecoded();
    } catch (err: any) {
      setDecodeError(err.message || 'Failed to decode VIN');
    } finally {
      setIsDecoding(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!vinDecodeData) {
    return (
      <div className="space-y-4">
        <div className="border border-gray-200 rounded-lg p-6">
          <div className="text-center">
            <svg className="w-16 h-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-4 text-lg font-semibold text-gray-900">VIN Not Decoded</h3>
            <p className="mt-2 text-sm text-gray-500">
              This vehicle's VIN has not been decoded yet. Decode the VIN to retrieve detailed vehicle information from NHTSA.
            </p>
            <div className="mt-6">
              <button
                onClick={handleDecode}
                disabled={isDecoding}
                className="px-6 py-2.5 text-sm font-medium text-white rounded transition-colors disabled:opacity-50"
                style={{ backgroundColor: '#7ed321' }}
              >
                {isDecoding ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Decoding VIN...
                  </span>
                ) : (
                  'Decode VIN'
                )}
              </button>
            </div>
            {decodeError && (
              <div className="mt-4 p-3 rounded bg-red-50 border border-red-200">
                <p className="text-sm text-red-600">{decodeError}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Decode Status */}
      <div className="border border-gray-200 rounded-lg p-4 bg-green-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-gray-900">VIN Decoded</p>
              <p className="text-xs text-gray-600">Last decoded: {formatDate(vinDecodeData.decoded_at)}</p>
            </div>
          </div>
          <button
            onClick={handleDecode}
            disabled={isDecoding}
            className="px-4 py-2 text-sm font-medium border border-gray-300 rounded hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            {isDecoding ? 'Re-decoding...' : 'Re-decode VIN'}
          </button>
        </div>
      </div>

      {/* Basic Info */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Basic Information</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">VIN</dt>
            <dd className="mt-0.5 text-sm text-gray-900 font-mono">{vinDecodeData.vin}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Model Year</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.model_year || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Make</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.make || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Model</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.model || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Manufacturer</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.manufacturer || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Vehicle Type</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.vehicle_type || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Body Class</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.body_class || '—'}</dd>
          </div>
        </div>
      </div>

      {/* Engine & Drivetrain */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Engine & Drivetrain</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Engine Model</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.engine_model || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Configuration</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.engine_configuration || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Cylinders</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.engine_cylinders || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Displacement</dt>
            <dd className="mt-0.5 text-sm text-gray-900">
              {vinDecodeData.displacement_liters ? `${vinDecodeData.displacement_liters}L` : '—'}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Primary Fuel</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.fuel_type_primary || '—'}</dd>
          </div>
          {vinDecodeData.fuel_type_secondary && (
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">Secondary Fuel</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.fuel_type_secondary}</dd>
            </div>
          )}
        </div>
      </div>

      {/* Ratings & Capacity */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Ratings & Capacity</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">GVWR</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.gvwr || '—'}</dd>
          </div>
          {vinDecodeData.gvwr_min_lbs && (
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">GVWR Min</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.gvwr_min_lbs.toLocaleString()} lbs</dd>
            </div>
          )}
          {vinDecodeData.gvwr_max_lbs && (
            <div>
              <dt className="text-xs font-medium text-gray-500 uppercase">GVWR Max</dt>
              <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.gvwr_max_lbs.toLocaleString()} lbs</dd>
            </div>
          )}
        </div>
      </div>

      {/* Safety & Equipment */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Safety & Equipment</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">ABS</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.abs || '—'}</dd>
          </div>
          <div className="col-span-2">
            <dt className="text-xs font-medium text-gray-500 uppercase">Airbag Locations</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.airbag_locations || '—'}</dd>
          </div>
        </div>
      </div>

      {/* Manufacturing */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wide mb-2">Manufacturing</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Plant City</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.plant_city || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Plant State</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.plant_state || '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 uppercase">Plant Country</dt>
            <dd className="mt-0.5 text-sm text-gray-900">{vinDecodeData.plant_country || '—'}</dd>
          </div>
        </div>
      </div>

      {/* Error Info (if any) */}
      {vinDecodeData.error_code && vinDecodeData.error_code !== '0' && (
        <div className="border border-red-200 rounded-lg p-4 bg-red-50">
          <h3 className="text-xs font-semibold text-red-900 uppercase tracking-wide mb-2">Decode Errors</h3>
          <p className="text-sm text-red-700">
            Error Code: {vinDecodeData.error_code}
            {vinDecodeData.error_text && ` - ${vinDecodeData.error_text}`}
          </p>
        </div>
      )}
    </div>
  );
}

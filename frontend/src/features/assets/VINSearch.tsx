/**
 * VINSearch - VIN lookup component
 *
 * Allows searching for vehicle information via VIN decode (NHTSA vPIC API)
 * Similar to USDOTSearch component
 */

import { useState } from 'react';
import { vinApi, type VINDecodeResult } from '@/api/vin.api';

interface VINSearchProps {
  onVINFound: (data: VINDecodeResult) => void;
  onSkip: () => void;
}

export function VINSearch({ onVINFound, onSkip }: VINSearchProps) {
  const [vin, setVin] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!vin.trim()) {
      setError('Please enter a VIN');
      return;
    }

    if (vin.trim().length !== 17) {
      setError('VIN must be exactly 17 characters');
      return;
    }

    setIsSearching(true);
    setError(null);

    try {
      // First check if we have cached decode data
      const cachedData = await vinApi.lookupByVIN(vin);

      if (cachedData) {
        // Use cached data
        onVINFound(cachedData);
        setIsSearching(false);
        return;
      }

      // No cached data, decode from NHTSA
      const data = await vinApi.decode(vin);

      // Check if decode was successful
      if (data.error_code && data.error_code !== '0') {
        setError(data.error_text || 'VIN decode failed');
        return;
      }

      onVINFound(data);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to decode VIN');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {/* Header */}
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-900">VIN Lookup</h2>
          <p className="mt-1 text-sm text-gray-600">
            Decode the VIN to auto-populate vehicle information
          </p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Vehicle Identification Number (VIN)
            </label>
            <input
              type="text"
              value={vin}
              onChange={(e) => setVin(e.target.value.toUpperCase())}
              placeholder="Enter 17-character VIN"
              maxLength={17}
              className="w-full px-3 py-2 border border-gray-300 rounded text-sm font-mono uppercase"
              disabled={isSearching}
            />
            <p className="mt-1 text-xs text-gray-500">
              The VIN can usually be found on the driver's side dashboard or door jamb
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between pt-4">
            <button
              type="button"
              onClick={onSkip}
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              Skip VIN Lookup →
            </button>
            <button
              type="submit"
              disabled={isSearching || !vin.trim()}
              className="px-6 py-2 text-sm font-medium text-white rounded transition-colors disabled:opacity-50"
              style={{ backgroundColor: '#7ed321' }}
            >
              {isSearching ? 'Decoding VIN...' : 'Decode VIN'}
            </button>
          </div>
        </form>

        {/* Info Box */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
          <div className="flex gap-3">
            <svg className="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-1">VIN Decode Information</p>
              <p className="text-blue-800">
                The VIN will be decoded using the NHTSA vPIC database. This will automatically
                populate year, make, model, and other vehicle details. You can still edit
                these fields after decoding.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * USDOTSearch Organism
 *
 * USDOT/MC number lookup with results display.
 * NO MOCK DATA - See DATA_CONTRACT.md
 */

import { useState, FormEvent } from 'react';
import { TextInput } from '@/components/atoms/TextInput';
import { FormField } from '@/components/molecules/FormField';
import { usdotApi, type USDOTProfile } from '@/api/usdot.api';

interface USDOTSearchProps {
  onProfileFound: (profile: USDOTProfile) => void;
  onManualEntry: () => void;
}

export function USDOTSearch({ onProfileFound, onManualEntry }: USDOTSearchProps) {
  const [searchType, setSearchType] = useState<'usdot' | 'mc'>('usdot');
  const [searchValue, setSearchValue] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<USDOTProfile | null>(null);

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();

    if (!searchValue.trim()) {
      setError('Please enter a number to search');
      return;
    }

    setIsSearching(true);
    setError(null);
    setProfile(null);

    try {
      const result = searchType === 'usdot'
        ? await usdotApi.lookupByUSDOT(searchValue.trim())
        : await usdotApi.lookupByMC(searchValue.trim());

      setProfile(result);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError(`${searchType.toUpperCase()} number not found in our database`);
      } else {
        setError(err.response?.data?.error || 'Failed to lookup profile');
      }
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-2" style={{ color: '#111827' }}>
          Lookup Customer by USDOT or MC Number
        </h2>
        <p style={{ color: '#6b7280' }}>
          Search for existing FMCSA data to pre-populate customer information
        </p>
      </div>

      <form onSubmit={handleSearch} className="mb-8">
        <div className="flex gap-4 items-end">
          <div style={{ width: '150px' }}>
            <FormField label="Search By" htmlFor="search_type">
              <select
                id="search_type"
                value={searchType}
                onChange={(e) => setSearchType(e.target.value as 'usdot' | 'mc')}
                className="w-full px-4 py-2 rounded-lg border"
                style={{
                  borderColor: '#d1d5db',
                  fontSize: '15px',
                  backgroundColor: 'white'
                }}
                disabled={isSearching}
              >
                <option value="usdot">USDOT</option>
                <option value="mc">MC Number</option>
              </select>
            </FormField>
          </div>

          <div className="flex-1">
            <FormField label={searchType === 'usdot' ? 'USDOT Number' : 'MC Number'} htmlFor="search_value">
              <TextInput
                id="search_value"
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder={searchType === 'usdot' ? 'Enter USDOT number' : 'Enter MC number'}
                disabled={isSearching}
              />
            </FormField>
          </div>

          <button
            type="submit"
            className="px-6 py-2 rounded-lg font-medium text-white mb-5"
            style={{
              backgroundColor: isSearching ? '#9ca3af' : '#7ed321',
              cursor: isSearching ? 'not-allowed' : 'pointer',
              height: '42px'
            }}
            disabled={isSearching}
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 rounded-lg" style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca' }}>
          <p className="font-medium mb-2" style={{ color: '#dc2626' }}>
            {error}
          </p>
          <button
            onClick={onManualEntry}
            className="text-sm font-medium hover:underline"
            style={{ color: '#dc2626' }}
          >
            Continue with manual entry →
          </button>
        </div>
      )}

      {/* Profile Found */}
      {profile && (
        <div className="bg-white border rounded-lg p-6" style={{ borderColor: '#bbf7d0', backgroundColor: '#f0fdf4' }}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold" style={{ color: '#15803d' }}>
                Profile Found
              </h3>
              <p className="text-sm" style={{ color: '#166534' }}>
                Last updated: {new Date(profile.lookup_date).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
            <div>
              <p className="font-medium" style={{ color: '#166534' }}>Legal Name</p>
              <p style={{ color: '#15803d' }}>{profile.legal_name || 'N/A'}</p>
            </div>
            <div>
              <p className="font-medium" style={{ color: '#166534' }}>DBA Name</p>
              <p style={{ color: '#15803d' }}>{profile.dba_name || 'N/A'}</p>
            </div>
            <div>
              <p className="font-medium" style={{ color: '#166534' }}>USDOT Number</p>
              <p style={{ color: '#15803d' }}>{profile.usdot_number}</p>
            </div>
            <div>
              <p className="font-medium" style={{ color: '#166534' }}>MC Number</p>
              <p style={{ color: '#15803d' }}>{profile.mc_number || 'N/A'}</p>
            </div>
            <div>
              <p className="font-medium" style={{ color: '#166534' }}>Physical Address</p>
              <p style={{ color: '#15803d' }}>
                {profile.physical_address && `${profile.physical_address}, `}
                {profile.physical_city && `${profile.physical_city}, `}
                {profile.physical_state} {profile.physical_zip}
              </p>
            </div>
            <div>
              <p className="font-medium" style={{ color: '#166534' }}>Safety Rating</p>
              <p style={{ color: '#15803d' }}>{profile.safety_rating || 'N/A'}</p>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => onProfileFound(profile)}
              className="px-6 py-2 rounded-lg font-medium text-white"
              style={{ backgroundColor: '#15803d' }}
            >
              Use This Data
            </button>
            <button
              onClick={onManualEntry}
              className="px-6 py-2 rounded-lg font-medium border"
              style={{ borderColor: '#d1d5db', color: '#374151' }}
            >
              Enter Manually Instead
            </button>
          </div>
        </div>
      )}

      {/* Skip Lookup */}
      {!profile && !error && (
        <div className="text-center">
          <button
            onClick={onManualEntry}
            className="text-sm font-medium hover:underline"
            style={{ color: '#6b7280' }}
          >
            Skip lookup and enter customer information manually →
          </button>
        </div>
      )}
    </div>
  );
}

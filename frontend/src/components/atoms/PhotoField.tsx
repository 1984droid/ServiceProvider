/**
 * PhotoField Atom
 *
 * Reusable photo upload component with preview
 * Used for PHOTO/ATTACHMENTS field type in inspection templates
 */

import { useState, useRef } from 'react';

interface Photo {
  id?: string;
  url: string;
  file?: File;
}

interface PhotoFieldProps {
  value: Photo[];
  onChange: (value: Photo[]) => void;
  disabled?: boolean;
  multiple?: boolean;
  maxPhotos?: number;
}

export function PhotoField({
  value = [],
  onChange,
  disabled = false,
  multiple = true,
  maxPhotos = 10
}: PhotoFieldProps) {

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [previews, setPreviews] = useState<Photo[]>(value);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    // Check max photos limit
    if (previews.length + files.length > maxPhotos) {
      alert(`Maximum ${maxPhotos} photos allowed`);
      return;
    }

    // Create preview URLs
    const newPhotos: Photo[] = files.map(file => ({
      url: URL.createObjectURL(file),
      file
    }));

    const updatedPhotos = multiple ? [...previews, ...newPhotos] : newPhotos;
    setPreviews(updatedPhotos);
    onChange(updatedPhotos);

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleRemove = (index: number) => {
    const photo = previews[index];
    // Revoke object URL to prevent memory leak
    if (photo.file) {
      URL.revokeObjectURL(photo.url);
    }

    const updatedPhotos = previews.filter((_, i) => i !== index);
    setPreviews(updatedPhotos);
    onChange(updatedPhotos);
  };

  return (
    <div className="space-y-3">
      {/* Photo Grid */}
      {previews.length > 0 && (
        <div className="grid grid-cols-3 gap-3">
          {previews.map((photo, index) => (
            <div key={index} className="relative group">
              <img
                src={photo.url}
                alt={`Photo ${index + 1}`}
                className="w-full h-24 object-cover rounded-lg border"
                style={{ borderColor: '#d1d5db' }}
              />
              {!disabled && (
                <button
                  type="button"
                  onClick={() => handleRemove(index)}
                  className="absolute top-1 right-1 w-6 h-6 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Upload Button */}
      {!disabled && (multiple || previews.length === 0) && previews.length < maxPhotos && (
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple={multiple}
            onChange={handleFileSelect}
            className="hidden"
            id="photo-upload"
          />
          <label
            htmlFor="photo-upload"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border cursor-pointer transition-colors"
            style={{
              borderColor: '#d1d5db',
              backgroundColor: 'white',
              color: '#374151'
            }}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="text-sm font-medium">
              {previews.length > 0 ? 'Add More Photos' : 'Add Photos'}
            </span>
          </label>
          <p className="mt-1 text-xs" style={{ color: '#6b7280' }}>
            {previews.length}/{maxPhotos} photos
          </p>
        </div>
      )}
    </div>
  );
}

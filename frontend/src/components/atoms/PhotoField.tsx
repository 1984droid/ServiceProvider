/**
 * PhotoField Atom
 *
 * Reusable photo upload component with preview
 * Immediately uploads photos to backend and displays thumbnails
 * Used for PHOTO/ATTACHMENTS field type in inspection templates
 */

import { useState, useRef, useEffect } from 'react';
import { inspectionsApi, type InspectionPhoto } from '@/api/inspections.api';
import { compressImage, formatFileSize } from '@/utils/imageCompression';

interface PhotoFieldProps {
  inspectionId: string;
  stepKey: string;
  defectId?: string;
  value: InspectionPhoto[];
  onChange: (value: InspectionPhoto[]) => void;
  disabled?: boolean;
  multiple?: boolean;
  maxPhotos?: number;
  showCaptions?: boolean;
}

interface PhotoState {
  photo?: InspectionPhoto;
  uploading?: boolean;
  error?: string;
  progress?: number;
  file?: File;
  previewUrl?: string;
}

export function PhotoField({
  inspectionId,
  stepKey,
  defectId,
  value = [],
  onChange,
  disabled = false,
  multiple = true,
  maxPhotos = 10,
  showCaptions = false,
}: PhotoFieldProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [photoStates, setPhotoStates] = useState<PhotoState[]>([]);

  // Initialize photo states from value
  useEffect(() => {
    setPhotoStates(value.map(photo => ({ photo })));
  }, [value]);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    // Check max photos limit
    if (photoStates.length + files.length > maxPhotos) {
      alert(`Maximum ${maxPhotos} photos allowed`);
      return;
    }

    // Add uploading states
    const newStates: PhotoState[] = files.map(file => ({
      uploading: true,
      file,
      previewUrl: URL.createObjectURL(file),
      progress: 0,
    }));

    const updatedStates = multiple ? [...photoStates, ...newStates] : newStates;
    setPhotoStates(updatedStates);

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }

    // Upload each file
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const stateIndex = photoStates.length + i;

      try {
        // Compress image
        const compressedFile = await compressImage(file, {
          maxWidth: 1920,
          maxHeight: 1920,
          quality: 0.85,
          maxSizeMB: 2,
        });

        // Upload
        const uploadedPhoto = await inspectionsApi.uploadPhoto(
          inspectionId,
          stepKey,
          compressedFile,
          { defectId, caption: '' }
        );

        // Update state with uploaded photo
        setPhotoStates(prev => {
          const newStates = [...prev];
          // Revoke preview URL
          if (newStates[stateIndex].previewUrl) {
            URL.revokeObjectURL(newStates[stateIndex].previewUrl!);
          }
          newStates[stateIndex] = { photo: uploadedPhoto };
          return newStates;
        });

        // Update parent with completed photos
        onChange(updatedStates.filter(s => s.photo).map(s => s.photo!).concat([uploadedPhoto]));

      } catch (error: any) {
        console.error('Photo upload failed:', error);

        // Update state with error
        setPhotoStates(prev => {
          const newStates = [...prev];
          newStates[stateIndex] = {
            ...newStates[stateIndex],
            uploading: false,
            error: error.response?.data?.error || error.message || 'Upload failed',
          };
          return newStates;
        });
      }
    }
  };

  const handleRemove = async (index: number) => {
    const state = photoStates[index];

    // If photo is uploaded, delete from backend
    if (state.photo) {
      try {
        await inspectionsApi.deletePhoto(inspectionId, state.photo.id);
      } catch (error) {
        console.error('Failed to delete photo:', error);
        alert('Failed to delete photo. Please try again.');
        return;
      }
    }

    // Revoke preview URL if exists
    if (state.previewUrl) {
      URL.revokeObjectURL(state.previewUrl);
    }

    // Update states
    const updatedStates = photoStates.filter((_, i) => i !== index);
    setPhotoStates(updatedStates);

    // Update parent
    onChange(updatedStates.filter(s => s.photo).map(s => s.photo!));
  };

  const handleRetry = (index: number) => {
    const state = photoStates[index];
    if (!state.file) return;

    // Create synthetic file input event
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(state.file);

    // Remove failed state
    setPhotoStates(prev => prev.filter((_, i) => i !== index));

    // Trigger upload
    handleFileSelect({
      target: { files: dataTransfer.files },
    } as any);
  };

  const handleCaptionChange = async (index: number, caption: string) => {
    const state = photoStates[index];
    if (!state.photo) return;

    // Update local state immediately for responsiveness
    setPhotoStates(prev => {
      const newStates = [...prev];
      newStates[index] = {
        ...newStates[index],
        photo: { ...state.photo!, caption },
      };
      return newStates;
    });

    // TODO: Add API endpoint to update caption
    // For now, caption is only set on upload
  };

  return (
    <div className="space-y-3">
      {/* Photo Grid */}
      {photoStates.length > 0 && (
        <div className="grid grid-cols-3 gap-3">
          {photoStates.map((state, index) => (
            <div key={index} className="relative group">
              {/* Image Preview */}
              <div className="relative w-full h-24 rounded-lg border overflow-hidden" style={{ borderColor: '#d1d5db' }}>
                <img
                  src={state.photo?.thumbnail_url || state.previewUrl || ''}
                  alt={state.photo?.caption || `Photo ${index + 1}`}
                  className="w-full h-full object-cover"
                />

                {/* Upload Progress Overlay */}
                {state.uploading && (
                  <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <div className="text-white text-xs">
                      <svg className="animate-spin h-5 w-5 mx-auto mb-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Uploading...
                    </div>
                  </div>
                )}

                {/* Error Overlay */}
                {state.error && (
                  <div className="absolute inset-0 bg-red-500 bg-opacity-90 flex flex-col items-center justify-center p-2">
                    <svg className="w-5 h-5 text-white mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-white text-xs text-center">{state.error}</span>
                  </div>
                )}
              </div>

              {/* Actions */}
              {!disabled && (
                <div className="absolute top-1 right-1 flex gap-1">
                  {state.error && (
                    <button
                      type="button"
                      onClick={() => handleRetry(index)}
                      className="w-6 h-6 bg-blue-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs"
                      title="Retry upload"
                    >
                      ↻
                    </button>
                  )}
                  {!state.uploading && (
                    <button
                      type="button"
                      onClick={() => handleRemove(index)}
                      className="w-6 h-6 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs"
                      title="Remove photo"
                    >
                      ×
                    </button>
                  )}
                </div>
              )}

              {/* Caption Input */}
              {showCaptions && state.photo && (
                <input
                  type="text"
                  value={state.photo.caption}
                  onChange={(e) => handleCaptionChange(index, e.target.value)}
                  placeholder="Add caption..."
                  disabled={disabled}
                  className="w-full mt-1 px-2 py-1 text-xs rounded border"
                  style={{ borderColor: '#d1d5db' }}
                />
              )}

              {/* File Size */}
              {state.photo && (
                <div className="mt-1 text-xs text-gray-500">
                  {formatFileSize(state.photo.file_size)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Upload Button */}
      {!disabled && (multiple || photoStates.length === 0) && photoStates.length < maxPhotos && (
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            multiple={multiple}
            onChange={handleFileSelect}
            className="hidden"
            id={`photo-upload-${stepKey}`}
          />
          <label
            htmlFor={`photo-upload-${stepKey}`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border cursor-pointer transition-colors hover:bg-gray-50"
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
              {photoStates.length > 0 ? 'Add More Photos' : 'Add Photos'}
            </span>
          </label>
          <p className="mt-1 text-xs" style={{ color: '#6b7280' }}>
            {photoStates.length}/{maxPhotos} photos
            {photoStates.length < maxPhotos && ' • Max 2MB per photo'}
          </p>
        </div>
      )}
    </div>
  );
}

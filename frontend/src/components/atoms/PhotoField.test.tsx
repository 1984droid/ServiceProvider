/**
 * Tests for PhotoField Component
 *
 * Following data contract - no hardcoded values
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PhotoField } from './PhotoField';
import { inspectionsApi } from '@/api/inspections.api';
import type { InspectionPhoto } from '@/api/inspections.api';
import * as imageCompression from '@/utils/imageCompression';

// Mock dependencies
vi.mock('@/api/inspections.api', () => ({
  inspectionsApi: {
    uploadPhoto: vi.fn(),
    deletePhoto: vi.fn(),
  },
}));

vi.mock('@/utils/imageCompression', () => ({
  compressImage: vi.fn((file) => Promise.resolve(file)),
  formatFileSize: vi.fn((bytes) => `${bytes} B`),
}));

// Test data factories
const createMockInspectionPhoto = (overrides: Partial<InspectionPhoto> = {}): InspectionPhoto => ({
  id: crypto.randomUUID(),
  inspection: crypto.randomUUID(),
  defect: null,
  step_key: 'visual_inspection',
  image: '/media/inspections/photo.jpg',
  thumbnail: '/media/inspections/thumb_photo.jpg',
  url: `http://localhost:8000/media/inspections/${crypto.randomUUID()}.jpg`,
  thumbnail_url: `http://localhost:8000/media/inspections/thumb_${crypto.randomUUID()}.jpg`,
  caption: '',
  file_size: 1024 * 500,
  width: 1920,
  height: 1080,
  uploaded_by: null,
  uploaded_by_name: null,
  created_at: new Date().toISOString(),
  ...overrides,
});

const createMockFile = (options: {
  name?: string;
  size?: number;
  type?: string;
} = {}) => {
  const {
    name = 'test-photo.jpg',
    size = 1024 * 1024,
    type = 'image/jpeg',
  } = options;

  return new File(['x'.repeat(size)], name, { type });
};

describe('PhotoField', () => {
  const defaultProps = {
    inspectionId: crypto.randomUUID(),
    stepKey: 'visual_inspection',
    value: [] as InspectionPhoto[],
    onChange: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render upload button when no photos', () => {
      render(<PhotoField {...defaultProps} />);

      expect(screen.getByText('Add Photos')).toBeInTheDocument();
    });

    it('should display existing photos', () => {
      const photos = [
        createMockInspectionPhoto(),
        createMockInspectionPhoto(),
      ];

      render(<PhotoField {...defaultProps} value={photos} />);

      const images = screen.getAllByRole('img');
      expect(images).toHaveLength(photos.length);
    });

    it('should show photo count', () => {
      const photos = [createMockInspectionPhoto()];

      render(<PhotoField {...defaultProps} value={photos} maxPhotos={10} />);

      expect(screen.getByText(/1\/10 photos/)).toBeInTheDocument();
    });

    it('should hide upload button when max photos reached', () => {
      const maxPhotos = 3;
      const photos = Array.from({ length: maxPhotos }, () =>
        createMockInspectionPhoto()
      );

      render(<PhotoField {...defaultProps} value={photos} maxPhotos={maxPhotos} />);

      expect(screen.queryByText('Add Photos')).not.toBeInTheDocument();
      expect(screen.queryByText('Add More Photos')).not.toBeInTheDocument();
    });

    it('should hide upload button when disabled prop is true', () => {
      render(<PhotoField {...defaultProps} disabled={true} />);

      // Upload button should not be visible when disabled
      expect(screen.queryByText('Add Photos')).not.toBeInTheDocument();
      expect(screen.queryByText('Add More Photos')).not.toBeInTheDocument();
    });
  });

  describe('Photo Upload', () => {
    it('should upload photo on file selection', async () => {
      const user = userEvent.setup();
      const mockPhoto = createMockInspectionPhoto();
      vi.mocked(inspectionsApi.uploadPhoto).mockResolvedValue(mockPhoto);

      render(<PhotoField {...defaultProps} />);

      const file = createMockFile();
      const input = screen.getByLabelText(/add photos/i).closest('input') as HTMLInputElement;

      await user.upload(input, file);

      await waitFor(() => {
        expect(inspectionsApi.uploadPhoto).toHaveBeenCalledWith(
          defaultProps.inspectionId,
          defaultProps.stepKey,
          file,
          expect.objectContaining({
            defectId: undefined,
            caption: '',
          })
        );
      });
    });

    it('should compress image before upload', async () => {
      const user = userEvent.setup();
      const mockPhoto = createMockInspectionPhoto();
      const compressedFile = createMockFile({ name: 'compressed.jpg' });

      vi.mocked(imageCompression.compressImage).mockResolvedValue(compressedFile);
      vi.mocked(inspectionsApi.uploadPhoto).mockResolvedValue(mockPhoto);

      render(<PhotoField {...defaultProps} />);

      const file = createMockFile({ size: 5 * 1024 * 1024 }); // 5MB
      const input = screen.getByLabelText(/add photos/i).closest('input') as HTMLInputElement;

      await user.upload(input, file);

      await waitFor(() => {
        expect(imageCompression.compressImage).toHaveBeenCalledWith(
          file,
          expect.objectContaining({
            maxWidth: 1920,
            maxHeight: 1920,
            quality: 0.85,
            maxSizeMB: 2,
          })
        );
      });
    });

    it('should show loading state during upload', async () => {
      const user = userEvent.setup();
      let resolveUpload: (value: InspectionPhoto) => void;
      const uploadPromise = new Promise<InspectionPhoto>((resolve) => {
        resolveUpload = resolve;
      });

      vi.mocked(inspectionsApi.uploadPhoto).mockReturnValue(uploadPromise);

      render(<PhotoField {...defaultProps} />);

      const file = createMockFile();
      const input = screen.getByLabelText(/add photos/i).closest('input') as HTMLInputElement;

      await user.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText('Uploading...')).toBeInTheDocument();
      });

      resolveUpload!(createMockInspectionPhoto());
    });

    it('should call onChange with uploaded photo', async () => {
      const user = userEvent.setup();
      const mockPhoto = createMockInspectionPhoto();
      const onChange = vi.fn();

      vi.mocked(inspectionsApi.uploadPhoto).mockResolvedValue(mockPhoto);

      render(<PhotoField {...defaultProps} onChange={onChange} />);

      const file = createMockFile();
      const input = screen.getByLabelText(/add photos/i).closest('input') as HTMLInputElement;

      await user.upload(input, file);

      await waitFor(() => {
        expect(onChange).toHaveBeenCalledWith(
          expect.arrayContaining([mockPhoto])
        );
      });
    });

    it('should include defectId when provided', async () => {
      const user = userEvent.setup();
      const defectId = crypto.randomUUID();
      const mockPhoto = createMockInspectionPhoto({ defect: defectId });

      vi.mocked(inspectionsApi.uploadPhoto).mockResolvedValue(mockPhoto);

      render(<PhotoField {...defaultProps} defectId={defectId} />);

      const file = createMockFile();
      const input = screen.getByLabelText(/add photos/i).closest('input') as HTMLInputElement;

      await user.upload(input, file);

      await waitFor(() => {
        expect(inspectionsApi.uploadPhoto).toHaveBeenCalledWith(
          expect.any(String),
          expect.any(String),
          expect.any(File),
          expect.objectContaining({ defectId })
        );
      });
    });

    it('should upload multiple photos when multiple=true', async () => {
      const user = userEvent.setup();
      const mockPhotos = [
        createMockInspectionPhoto(),
        createMockInspectionPhoto(),
      ];

      vi.mocked(inspectionsApi.uploadPhoto)
        .mockResolvedValueOnce(mockPhotos[0])
        .mockResolvedValueOnce(mockPhotos[1]);

      render(<PhotoField {...defaultProps} multiple={true} />);

      const files = [createMockFile(), createMockFile()];
      const input = screen.getByLabelText(/add photos/i).closest('input') as HTMLInputElement;

      await user.upload(input, files);

      await waitFor(() => {
        expect(inspectionsApi.uploadPhoto).toHaveBeenCalledTimes(files.length);
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error message when upload fails', async () => {
      const user = userEvent.setup();
      const errorMessage = 'Upload failed - network error';

      vi.mocked(inspectionsApi.uploadPhoto).mockRejectedValue(
        new Error(errorMessage)
      );

      render(<PhotoField {...defaultProps} />);

      const file = createMockFile();
      const input = screen.getByLabelText(/add photos/i).closest('input') as HTMLInputElement;

      await user.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText(/upload failed/i)).toBeInTheDocument();
      });
    });

    it('should show retry button on upload failure', async () => {
      const user = userEvent.setup();

      vi.mocked(inspectionsApi.uploadPhoto).mockRejectedValue(
        new Error('Upload failed')
      );

      render(<PhotoField {...defaultProps} />);

      const file = createMockFile();
      const input = screen.getByLabelText(/add photos/i).closest('input') as HTMLInputElement;

      await user.upload(input, file);

      await waitFor(() => {
        expect(screen.getByTitle('Retry upload')).toBeInTheDocument();
      });
    });

    it('should enforce max photo limit', async () => {
      const user = userEvent.setup();
      const maxPhotos = 2;
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      render(<PhotoField {...defaultProps} maxPhotos={maxPhotos} />);

      const files = Array.from({ length: maxPhotos + 1 }, () => createMockFile());
      const input = screen.getByLabelText(/add photos/i).closest('input') as HTMLInputElement;

      await user.upload(input, files);

      expect(alertSpy).toHaveBeenCalledWith(`Maximum ${maxPhotos} photos allowed`);
      alertSpy.mockRestore();
    });
  });

  describe('Photo Deletion', () => {
    it('should delete photo when remove button clicked', async () => {
      const user = userEvent.setup();
      const photo = createMockInspectionPhoto();
      const onChange = vi.fn();

      vi.mocked(inspectionsApi.deletePhoto).mockResolvedValue();

      render(<PhotoField {...defaultProps} value={[photo]} onChange={onChange} />);

      const removeButton = screen.getByTitle('Remove photo');
      await user.click(removeButton);

      await waitFor(() => {
        expect(inspectionsApi.deletePhoto).toHaveBeenCalledWith(
          defaultProps.inspectionId,
          photo.id
        );
      });

      expect(onChange).toHaveBeenCalledWith([]);
    });

    it('should show alert when deletion fails', async () => {
      const user = userEvent.setup();
      const photo = createMockInspectionPhoto();
      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

      vi.mocked(inspectionsApi.deletePhoto).mockRejectedValue(
        new Error('Delete failed')
      );

      render(<PhotoField {...defaultProps} value={[photo]} />);

      const removeButton = screen.getByTitle('Remove photo');
      await user.click(removeButton);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith(
          'Failed to delete photo. Please try again.'
        );
      });

      alertSpy.mockRestore();
    });
  });

  describe('Caption Support', () => {
    it('should show caption inputs when showCaptions=true', () => {
      const photo = createMockInspectionPhoto({ caption: 'Test caption' });

      render(<PhotoField {...defaultProps} value={[photo]} showCaptions={true} />);

      const captionInput = screen.getByDisplayValue('Test caption');
      expect(captionInput).toBeInTheDocument();
    });

    it('should not show caption inputs when showCaptions=false', () => {
      const photo = createMockInspectionPhoto({ caption: 'Test caption' });

      render(<PhotoField {...defaultProps} value={[photo]} showCaptions={false} />);

      expect(screen.queryByDisplayValue('Test caption')).not.toBeInTheDocument();
    });
  });

  describe('File Size Display', () => {
    it('should display file size for each photo', () => {
      const fileSize = 1024 * 500;
      const photo = createMockInspectionPhoto({ file_size: fileSize });

      vi.mocked(imageCompression.formatFileSize).mockReturnValue('500.0 KB');

      render(<PhotoField {...defaultProps} value={[photo]} />);

      expect(imageCompression.formatFileSize).toHaveBeenCalledWith(fileSize);
      expect(screen.getByText('500.0 KB')).toBeInTheDocument();
    });
  });

  describe('Mobile Camera Support', () => {
    it('should have capture attribute for mobile camera access', () => {
      render(<PhotoField {...defaultProps} />);

      const input = screen.getByLabelText(/add photos/i).closest('input') as HTMLInputElement;
      expect(input).toHaveAttribute('capture', 'environment');
    });
  });
});

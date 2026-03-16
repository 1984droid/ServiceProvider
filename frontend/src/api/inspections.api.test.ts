/**
 * Tests for Inspections API - Photo Methods
 *
 * Following data contract - no hardcoded values
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { inspectionsApi } from './inspections.api';
import type { InspectionPhoto } from './inspections.api';
import { apiClient } from '@/lib/axios';

// Mock axios
vi.mock('@/lib/axios', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
  },
}));

// Test data factories
const createMockInspectionPhoto = (overrides: Partial<InspectionPhoto> = {}): InspectionPhoto => ({
  id: crypto.randomUUID(),
  inspection: crypto.randomUUID(),
  defect: null,
  step_key: 'visual_inspection',
  image: '/media/inspections/photo.jpg',
  thumbnail: '/media/inspections/thumb_photo.jpg',
  url: 'http://localhost:8000/media/inspections/photo.jpg',
  thumbnail_url: 'http://localhost:8000/media/inspections/thumb_photo.jpg',
  caption: '',
  file_size: 1024 * 500, // 500KB
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

  const blob = new Blob(['x'.repeat(size)], { type });
  return new File([blob], name, { type });
};

describe('inspectionsApi - Photo Methods', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('uploadPhoto', () => {
    it('should upload photo with required parameters', async () => {
      const mockPhoto = createMockInspectionPhoto();
      const inspectionId = crypto.randomUUID();
      const stepKey = 'visual_inspection';
      const file = createMockFile();

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockPhoto });

      const result = await inspectionsApi.uploadPhoto(inspectionId, stepKey, file);

      expect(apiClient.post).toHaveBeenCalledWith(
        `/inspections/${inspectionId}/upload_photo/`,
        expect.any(FormData),
        expect.objectContaining({
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
      );

      const formData = vi.mocked(apiClient.post).mock.calls[0][1] as FormData;
      expect(formData.get('image')).toBe(file);
      expect(formData.get('step_key')).toBe(stepKey);

      expect(result).toEqual(mockPhoto);
    });

    it('should include optional caption', async () => {
      const mockPhoto = createMockInspectionPhoto({ caption: 'Test caption' });
      const inspectionId = crypto.randomUUID();
      const stepKey = 'visual_inspection';
      const file = createMockFile();
      const caption = 'Test caption';

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockPhoto });

      await inspectionsApi.uploadPhoto(inspectionId, stepKey, file, { caption });

      const formData = vi.mocked(apiClient.post).mock.calls[0][1] as FormData;
      expect(formData.get('caption')).toBe(caption);
    });

    it('should include optional defect ID', async () => {
      const defectId = crypto.randomUUID();
      const mockPhoto = createMockInspectionPhoto({ defect: defectId });
      const inspectionId = crypto.randomUUID();
      const stepKey = 'visual_inspection';
      const file = createMockFile();

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockPhoto });

      await inspectionsApi.uploadPhoto(inspectionId, stepKey, file, { defectId });

      const formData = vi.mocked(apiClient.post).mock.calls[0][1] as FormData;
      expect(formData.get('defect_id')).toBe(defectId);
    });

    it('should handle upload errors', async () => {
      const inspectionId = crypto.randomUUID();
      const stepKey = 'visual_inspection';
      const file = createMockFile();
      const error = new Error('Upload failed');

      vi.mocked(apiClient.post).mockRejectedValue(error);

      await expect(
        inspectionsApi.uploadPhoto(inspectionId, stepKey, file)
      ).rejects.toThrow('Upload failed');
    });
  });

  describe('listPhotos', () => {
    it('should list all photos for an inspection', async () => {
      const inspectionId = crypto.randomUUID();
      const mockPhotos = [
        createMockInspectionPhoto(),
        createMockInspectionPhoto(),
        createMockInspectionPhoto(),
      ];
      const mockResponse = {
        count: mockPhotos.length,
        photos: mockPhotos,
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await inspectionsApi.listPhotos(inspectionId);

      expect(apiClient.get).toHaveBeenCalledWith(
        `/inspections/${inspectionId}/photos/`,
        { params: undefined }
      );

      expect(result).toEqual(mockResponse);
      expect(result.count).toBe(mockPhotos.length);
      expect(result.photos).toHaveLength(mockPhotos.length);
    });

    it('should filter photos by step_key', async () => {
      const inspectionId = crypto.randomUUID();
      const stepKey = 'boom_inspection';
      const mockPhotos = [createMockInspectionPhoto({ step_key: stepKey })];
      const mockResponse = {
        count: mockPhotos.length,
        photos: mockPhotos,
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await inspectionsApi.listPhotos(inspectionId, { step_key: stepKey });

      expect(apiClient.get).toHaveBeenCalledWith(
        `/inspections/${inspectionId}/photos/`,
        { params: { step_key: stepKey } }
      );

      expect(result.photos.every(p => p.step_key === stepKey)).toBe(true);
    });

    it('should filter photos by defect_id', async () => {
      const inspectionId = crypto.randomUUID();
      const defectId = crypto.randomUUID();
      const mockPhotos = [createMockInspectionPhoto({ defect: defectId })];
      const mockResponse = {
        count: mockPhotos.length,
        photos: mockPhotos,
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await inspectionsApi.listPhotos(inspectionId, { defect_id: defectId });

      expect(apiClient.get).toHaveBeenCalledWith(
        `/inspections/${inspectionId}/photos/`,
        { params: { defect_id: defectId } }
      );

      expect(result.photos.every(p => p.defect === defectId)).toBe(true);
    });

    it('should return empty list when no photos exist', async () => {
      const inspectionId = crypto.randomUUID();
      const mockResponse = {
        count: 0,
        photos: [],
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await inspectionsApi.listPhotos(inspectionId);

      expect(result.count).toBe(0);
      expect(result.photos).toEqual([]);
    });

    it('should handle fetch errors', async () => {
      const inspectionId = crypto.randomUUID();
      const error = new Error('Network error');

      vi.mocked(apiClient.get).mockRejectedValue(error);

      await expect(
        inspectionsApi.listPhotos(inspectionId)
      ).rejects.toThrow('Network error');
    });
  });

  describe('deletePhoto', () => {
    it('should delete photo by ID', async () => {
      const inspectionId = crypto.randomUUID();
      const photoId = crypto.randomUUID();

      vi.mocked(apiClient.delete).mockResolvedValue({});

      await inspectionsApi.deletePhoto(inspectionId, photoId);

      expect(apiClient.delete).toHaveBeenCalledWith(
        `/inspections/${inspectionId}/photos/${photoId}/`
      );
    });

    it('should handle delete errors', async () => {
      const inspectionId = crypto.randomUUID();
      const photoId = crypto.randomUUID();
      const error = new Error('Delete failed');

      vi.mocked(apiClient.delete).mockRejectedValue(error);

      await expect(
        inspectionsApi.deletePhoto(inspectionId, photoId)
      ).rejects.toThrow('Delete failed');
    });

    it('should handle 404 errors for non-existent photos', async () => {
      const inspectionId = crypto.randomUUID();
      const photoId = crypto.randomUUID();
      const error = { response: { status: 404 } };

      vi.mocked(apiClient.delete).mockRejectedValue(error);

      await expect(
        inspectionsApi.deletePhoto(inspectionId, photoId)
      ).rejects.toEqual(error);
    });
  });

  describe('Photo data contract validation', () => {
    it('should return photo with all required fields', async () => {
      const mockPhoto = createMockInspectionPhoto();
      const inspectionId = crypto.randomUUID();
      const stepKey = 'visual_inspection';
      const file = createMockFile();

      vi.mocked(apiClient.post).mockResolvedValue({ data: mockPhoto });

      const result = await inspectionsApi.uploadPhoto(inspectionId, stepKey, file);

      // Verify all required fields are present
      expect(result).toHaveProperty('id');
      expect(result).toHaveProperty('inspection');
      expect(result).toHaveProperty('step_key');
      expect(result).toHaveProperty('url');
      expect(result).toHaveProperty('thumbnail_url');
      expect(result).toHaveProperty('file_size');
      expect(result).toHaveProperty('created_at');
    });

    it('should handle photos with different file sizes', async () => {
      const fileSizes = [100, 1024, 1024 * 1024, 1024 * 1024 * 5];

      for (const size of fileSizes) {
        const mockPhoto = createMockInspectionPhoto({ file_size: size });
        const inspectionId = crypto.randomUUID();
        const stepKey = 'visual_inspection';
        const file = createMockFile({ size });

        vi.mocked(apiClient.post).mockResolvedValue({ data: mockPhoto });

        const result = await inspectionsApi.uploadPhoto(inspectionId, stepKey, file);

        expect(result.file_size).toBe(size);
        expect(result.file_size).toBeGreaterThan(0);
      }
    });
  });
});

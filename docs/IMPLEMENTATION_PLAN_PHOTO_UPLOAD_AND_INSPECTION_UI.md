# Implementation Plan: Photo Upload/Storage & Frontend Inspection Execution UI

**Status:** Planning Phase
**Target:** Production Ready
**Priority:** High
**Estimated Effort:** 3-4 weeks (2 developers)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase 1: Photo Upload & Storage](#phase-1-photo-upload--storage)
3. [Phase 2: Frontend Inspection Execution UI](#phase-2-frontend-inspection-execution-ui)
4. [Testing Strategy](#testing-strategy)
5. [Deployment Plan](#deployment-plan)
6. [Success Metrics](#success-metrics)

---

## Executive Summary

### Current State
- ✅ Backend inspection execution is fully functional (148 tests passing)
- ✅ PhotoField component exists in frontend but stores only file objects (no upload)
- ✅ Defect schema supports `photo_evidence` field (array of strings)
- ✅ PDF export service has placeholder for photos
- ⚠️ No photo storage/upload implementation
- ⚠️ Frontend inspection UI is partially complete (basic step rendering exists)

### Goals
1. **Photo Upload & Storage**: Implement complete photo upload pipeline with S3/cloud storage
2. **Inspection UI**: Build production-ready inspection execution interface

### Business Value
- Inspectors can capture photo evidence during inspections (critical for compliance)
- Photos automatically included in PDF reports and work orders
- Improved defect documentation quality
- Mobile-friendly inspection workflow

---

## Phase 1: Photo Upload & Storage

**Duration:** 1.5-2 weeks
**Priority:** P0 (Blocking for production use)

### Architecture Decision: AWS S3 + CloudFront CDN

**Why S3:**
- Industry standard for object storage
- Scalable (unlimited storage)
- Cost-effective ($0.023/GB/month)
- Integrated with Django via `boto3` and `django-storages`
- Supports direct browser uploads (reducing server load)
- Versioning and lifecycle policies

**Why CloudFront:**
- Fast global content delivery
- Reduces S3 data transfer costs
- HTTPS by default
- Image transformation on-the-fly (optional)
- Caching reduces latency

**Alternative Considered:**
- Local filesystem storage → Not scalable, no CDN, backup challenges
- Azure Blob Storage → Similar to S3 but less Django ecosystem support
- Google Cloud Storage → Good alternative but S3 has better Django integration

---

### 1.1 Backend Implementation

#### 1.1.1 Install Dependencies

**File:** `requirements.txt`
```python
# Photo Storage
boto3>=1.34.0                    # AWS SDK for Python
django-storages[s3]>=1.14.0      # Django storage backends for S3
Pillow>=10.2.0                   # Image processing (resize, optimize)
```

#### 1.1.2 Django Settings Configuration

**File:** `service_provider/settings.py`
```python
# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'serviceprovider-inspections-prod')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN', f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com')

# CloudFront CDN (optional but recommended)
AWS_CLOUDFRONT_DOMAIN = os.getenv('AWS_CLOUDFRONT_DOMAIN', '')  # e.g., 'd111111abcdef8.cloudfront.net'
if AWS_CLOUDFRONT_DOMAIN:
    AWS_S3_CUSTOM_DOMAIN = AWS_CLOUDFRONT_DOMAIN

# S3 Object Parameters
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # 1 day cache
}

# S3 File Overwrite
AWS_S3_FILE_OVERWRITE = False  # Prevent overwriting files with same name
AWS_DEFAULT_ACL = 'private'     # Files are private by default
AWS_QUERYSTRING_AUTH = True     # Generate signed URLs for private files
AWS_QUERYSTRING_EXPIRE = 3600   # Signed URLs expire in 1 hour

# Media Files (Inspection Photos, Defect Evidence)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_ROOT = 'media/'

# Max Upload Size
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
```

**Environment Variables (.env):**
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=serviceprovider-inspections-prod
AWS_S3_REGION_NAME=us-east-1
AWS_CLOUDFRONT_DOMAIN=d111111abcdef8.cloudfront.net
```

#### 1.1.3 Photo Model

**File:** `apps/inspections/models.py`
```python
import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def inspection_photo_upload_path(instance, filename):
    """
    Generate upload path for inspection photos.

    Pattern: inspections/{inspection_id}/photos/{photo_id}_{filename}
    """
    ext = filename.split('.')[-1]
    filename = f"{instance.id}_{filename}"
    return f'inspections/{instance.inspection.id}/photos/{filename}'


class InspectionPhoto(BaseModel):
    """
    Photo attached to an inspection or defect.

    Photos are stored in S3 and served via CloudFront CDN.
    Automatic thumbnail generation for previews.
    """

    inspection = models.ForeignKey(
        'InspectionRun',
        on_delete=models.CASCADE,
        related_name='photos'
    )

    defect = models.ForeignKey(
        'InspectionDefect',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='photos',
        help_text='If photo is evidence for a defect'
    )

    step_key = models.CharField(
        max_length=100,
        help_text='Step where photo was captured'
    )

    image = models.ImageField(
        upload_to=inspection_photo_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic', 'webp'])
        ],
        help_text='Original photo file'
    )

    thumbnail = models.ImageField(
        upload_to=inspection_photo_upload_path,
        null=True,
        blank=True,
        help_text='Auto-generated thumbnail (300x300)'
    )

    caption = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional photo caption'
    )

    file_size = models.IntegerField(
        help_text='File size in bytes'
    )

    width = models.IntegerField(
        null=True,
        blank=True,
        help_text='Image width in pixels'
    )

    height = models.IntegerField(
        null=True,
        blank=True,
        help_text='Image height in pixels'
    )

    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_inspection_photos'
    )

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['inspection', 'step_key']),
            models.Index(fields=['defect']),
        ]

    def __str__(self):
        return f"Photo for {self.inspection} - {self.step_key}"

    def save(self, *args, **kwargs):
        """Auto-generate thumbnail on save."""
        if self.image and not self.thumbnail:
            self.thumbnail = self._create_thumbnail()

        # Extract image dimensions
        if self.image:
            img = Image.open(self.image)
            self.width, self.height = img.size
            self.file_size = self.image.size

        super().save(*args, **kwargs)

    def _create_thumbnail(self, size=(300, 300)):
        """Create thumbnail from original image."""
        img = Image.open(self.image)
        img.thumbnail(size, Image.Resampling.LANCZOS)

        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Save to BytesIO
        thumb_io = BytesIO()
        img.save(thumb_io, format='JPEG', quality=85, optimize=True)
        thumb_io.seek(0)

        # Create InMemoryUploadedFile
        thumb_file = InMemoryUploadedFile(
            thumb_io,
            None,
            f'thumb_{self.image.name}',
            'image/jpeg',
            thumb_io.getbuffer().nbytes,
            None
        )

        return thumb_file

    def get_signed_url(self, expiration=3600):
        """Generate signed URL for private photo access."""
        from django.core.files.storage import default_storage
        return default_storage.url(self.image.name)
```

**Update InspectionDefect Model:**
```python
class InspectionDefect(BaseModel):
    # ... existing fields ...

    @property
    def photo_urls(self):
        """Get list of photo URLs for this defect."""
        return [photo.get_signed_url() for photo in self.photos.all()]

    @property
    def photo_count(self):
        """Count photos attached to this defect."""
        return self.photos.count()
```

#### 1.1.4 Photo Serializer

**File:** `apps/inspections/serializers.py`
```python
from rest_framework import serializers
from .models import InspectionPhoto


class InspectionPhotoSerializer(serializers.ModelSerializer):
    """Serializer for inspection photos."""

    url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = InspectionPhoto
        fields = [
            'id',
            'inspection',
            'defect',
            'step_key',
            'image',
            'thumbnail',
            'url',
            'thumbnail_url',
            'caption',
            'file_size',
            'width',
            'height',
            'uploaded_by',
            'uploaded_by_name',
            'created_at',
        ]
        read_only_fields = ['id', 'file_size', 'width', 'height', 'created_at', 'thumbnail']

    def get_url(self, obj):
        """Get signed URL for full image."""
        return obj.get_signed_url()

    def get_thumbnail_url(self, obj):
        """Get signed URL for thumbnail."""
        if obj.thumbnail:
            from django.core.files.storage import default_storage
            return default_storage.url(obj.thumbnail.name)
        return None

    def get_uploaded_by_name(self, obj):
        """Get uploader's name."""
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.username
        return None


class PhotoUploadSerializer(serializers.Serializer):
    """Serializer for photo upload."""

    inspection_id = serializers.UUIDField()
    step_key = serializers.CharField(max_length=100)
    defect_id = serializers.UUIDField(required=False, allow_null=True)
    image = serializers.ImageField()
    caption = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_image(self, value):
        """Validate image file."""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image file size cannot exceed 10MB")

        # Check image format
        try:
            img = Image.open(value)
            img.verify()
        except Exception:
            raise serializers.ValidationError("Invalid image file")

        return value

    def validate_inspection_id(self, value):
        """Validate inspection exists and is editable."""
        from .models import InspectionRun
        try:
            inspection = InspectionRun.objects.get(id=value)
            if inspection.status == 'COMPLETED':
                raise serializers.ValidationError("Cannot upload photos to completed inspection")
            return value
        except InspectionRun.DoesNotExist:
            raise serializers.ValidationError("Inspection not found")
```

#### 1.1.5 Photo Upload API Endpoint

**File:** `apps/inspections/views.py`
```python
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import InspectionPhotoSerializer, PhotoUploadSerializer


class InspectionRunViewSet(viewsets.ModelViewSet):
    # ... existing code ...

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_photo(self, request, pk=None):
        """
        Upload photo to inspection.

        POST /api/inspections/{id}/upload_photo/

        Body (multipart/form-data):
        - image: Image file
        - step_key: Step where photo was captured
        - defect_id: (optional) Defect ID if photo is evidence
        - caption: (optional) Photo caption

        Returns:
            201: Photo uploaded successfully with signed URLs
            400: Validation error
            403: Cannot edit completed inspection
        """
        inspection = self.get_object()

        # Check permissions
        if inspection.status == 'COMPLETED':
            return Response(
                {'error': 'Cannot upload photos to completed inspection'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Prepare data
        data = {
            'inspection_id': inspection.id,
            'step_key': request.data.get('step_key'),
            'defect_id': request.data.get('defect_id'),
            'image': request.FILES.get('image'),
            'caption': request.data.get('caption', ''),
        }

        # Validate
        serializer = PhotoUploadSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create photo
        photo = InspectionPhoto.objects.create(
            inspection=inspection,
            step_key=serializer.validated_data['step_key'],
            defect_id=serializer.validated_data.get('defect_id'),
            image=serializer.validated_data['image'],
            caption=serializer.validated_data.get('caption', ''),
            uploaded_by=request.user
        )

        # Return photo data with signed URLs
        photo_serializer = InspectionPhotoSerializer(photo)
        return Response(photo_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """
        List all photos for inspection.

        GET /api/inspections/{id}/photos/
        Query params:
        - step_key: Filter by step
        - defect_id: Filter by defect

        Returns:
            200: List of photos with signed URLs
        """
        inspection = self.get_object()
        photos = inspection.photos.all()

        # Filter by step_key
        step_key = request.query_params.get('step_key')
        if step_key:
            photos = photos.filter(step_key=step_key)

        # Filter by defect
        defect_id = request.query_params.get('defect_id')
        if defect_id:
            photos = photos.filter(defect_id=defect_id)

        serializer = InspectionPhotoSerializer(photos, many=True)
        return Response({
            'count': len(serializer.data),
            'photos': serializer.data
        })

    @action(detail=False, methods=['delete'], url_path='photos/(?P<photo_id>[^/.]+)')
    def delete_photo(self, request, pk=None, photo_id=None):
        """
        Delete a photo.

        DELETE /api/inspections/{id}/photos/{photo_id}/

        Returns:
            204: Photo deleted
            403: Cannot delete from completed inspection
            404: Photo not found
        """
        inspection = self.get_object()

        try:
            photo = InspectionPhoto.objects.get(id=photo_id, inspection=inspection)
        except InspectionPhoto.DoesNotExist:
            return Response(
                {'error': 'Photo not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check permissions
        if inspection.status == 'COMPLETED':
            return Response(
                {'error': 'Cannot delete photos from completed inspection'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Delete from S3 and database
        photo.image.delete(save=False)
        if photo.thumbnail:
            photo.thumbnail.delete(save=False)
        photo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
```

#### 1.1.6 Database Migration

```bash
cd /c/NextGenProjects/ServiceProvider
python manage.py makemigrations inspections -n add_inspection_photos
python manage.py migrate
```

**Migration file:** `apps/inspections/migrations/000X_add_inspection_photos.py`

#### 1.1.7 Update Defect Schema to Include Photos

**File:** `apps/inspections/services/defect_to_work_order_service.py`
```python
class DefectToWorkOrderService:
    # ... existing code ...

    @classmethod
    def _build_work_description(cls, defect: InspectionDefect, vocab: Dict[str, str]) -> str:
        """
        Build comprehensive work order description from defect data.
        """
        parts = []

        # ... existing code ...

        # Photo Evidence (updated to use InspectionPhoto model)
        photo_count = defect.photo_count
        if photo_count > 0:
            parts.append("")
            parts.append(f"Photo Evidence: {photo_count} photo(s) attached")
            parts.append("Photos are attached to this work order and available in the inspection report PDF.")

        # ... rest of existing code ...
```

#### 1.1.8 Update PDF Export Service

**File:** `apps/inspections/services/pdf_export_service.py`
```python
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
import requests
from io import BytesIO


class InspectionPDFExporter:
    # ... existing code ...

    def _add_defect_photos(self, defect):
        """Add photos for a defect to the PDF."""
        photos = defect.photos.all()[:4]  # Max 4 photos per defect

        if not photos:
            return

        self.story.append(Spacer(1, 0.1 * inch))
        self.story.append(Paragraph("Photo Evidence:", self.styles['Heading3']))

        # Create photo grid (2x2)
        photo_data = []
        row = []

        for i, photo in enumerate(photos):
            # Download image from S3
            response = requests.get(photo.get_signed_url())
            img_data = BytesIO(response.content)

            # Resize to fit in PDF (2 inches square)
            img = PILImage.open(img_data)
            img.thumbnail((200, 200), PILImage.Resampling.LANCZOS)

            # Save to new BytesIO
            output = BytesIO()
            img.save(output, format='JPEG')
            output.seek(0)

            # Add to row
            row.append(Image(output, width=2*inch, height=2*inch))

            # Create new row after 2 images
            if (i + 1) % 2 == 0:
                photo_data.append(row)
                row = []

        # Add remaining photos
        if row:
            photo_data.append(row)

        # Create table
        if photo_data:
            photo_table = Table(photo_data, colWidths=[2.2*inch, 2.2*inch])
            photo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            self.story.append(photo_table)

    def _add_defects_section(self):
        """Generate defects summary section."""
        # ... existing code for defect listing ...

        for defect in defects:
            # ... existing defect details ...

            # Add photos
            self._add_defect_photos(defect)
```

---

### 1.2 Frontend Implementation

#### 1.2.1 Photo Upload API Client

**File:** `frontend/src/api/photos.api.ts`
```typescript
import axios from '@/lib/axios';

export interface Photo {
  id: string;
  inspection: string;
  defect?: string;
  step_key: string;
  url: string;
  thumbnail_url?: string;
  caption: string;
  file_size: number;
  width?: number;
  height?: number;
  uploaded_by?: string;
  uploaded_by_name?: string;
  created_at: string;
}

export interface PhotoUploadData {
  image: File;
  step_key: string;
  defect_id?: string;
  caption?: string;
}

export const photosApi = {
  /**
   * Upload photo to inspection
   */
  uploadPhoto: async (inspectionId: string, data: PhotoUploadData): Promise<Photo> => {
    const formData = new FormData();
    formData.append('image', data.image);
    formData.append('step_key', data.step_key);
    if (data.defect_id) {
      formData.append('defect_id', data.defect_id);
    }
    if (data.caption) {
      formData.append('caption', data.caption);
    }

    const response = await axios.post(
      `/api/inspections/${inspectionId}/upload_photo/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * List photos for inspection
   */
  listPhotos: async (
    inspectionId: string,
    filters?: { step_key?: string; defect_id?: string }
  ): Promise<{ count: number; photos: Photo[] }> => {
    const params = new URLSearchParams();
    if (filters?.step_key) params.append('step_key', filters.step_key);
    if (filters?.defect_id) params.append('defect_id', filters.defect_id);

    const response = await axios.get(
      `/api/inspections/${inspectionId}/photos/?${params.toString()}`
    );
    return response.data;
  },

  /**
   * Delete photo
   */
  deletePhoto: async (inspectionId: string, photoId: string): Promise<void> => {
    await axios.delete(`/api/inspections/${inspectionId}/photos/${photoId}/`);
  },
};
```

#### 1.2.2 Photo Upload Hook

**File:** `frontend/src/features/inspections/hooks/usePhotoUpload.ts`
```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { photosApi, type PhotoUploadData } from '@/api/photos.api';
import { toast } from '@/components/ui/Toast';

export function usePhotoUpload(inspectionId: string) {
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: (data: PhotoUploadData) => photosApi.uploadPhoto(inspectionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inspection-photos', inspectionId] });
      toast.success('Photo uploaded successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to upload photo');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (photoId: string) => photosApi.deletePhoto(inspectionId, photoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inspection-photos', inspectionId] });
      toast.success('Photo deleted');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to delete photo');
    },
  });

  return {
    uploadPhoto: uploadMutation.mutate,
    deletePhoto: deleteMutation.mutate,
    isUploading: uploadMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

export function useInspectionPhotos(inspectionId: string, stepKey?: string, defectId?: string) {
  return useQuery({
    queryKey: ['inspection-photos', inspectionId, stepKey, defectId],
    queryFn: () => photosApi.listPhotos(inspectionId, { step_key: stepKey, defect_id: defectId }),
  });
}
```

#### 1.2.3 Update PhotoField Component

**File:** `frontend/src/components/atoms/PhotoField.tsx`
```typescript
/**
 * PhotoField Atom - ENHANCED VERSION
 *
 * Supports both:
 * 1. Local file selection (existing inspection creation)
 * 2. Direct upload to S3 (during inspection execution)
 */

import { useState, useRef } from 'react';
import { usePhotoUpload } from '@/features/inspections/hooks/usePhotoUpload';
import type { Photo } from '@/api/photos.api';

interface PhotoFieldProps {
  // Existing mode (local files)
  value?: File[];
  onChange?: (value: File[]) => void;

  // New mode (S3 upload)
  inspectionId?: string;
  stepKey?: string;
  defectId?: string;
  photos?: Photo[];

  disabled?: boolean;
  multiple?: boolean;
  maxPhotos?: number;
  mode?: 'local' | 'upload';  // 'local' = existing behavior, 'upload' = S3 upload
}

export function PhotoField({
  value = [],
  onChange,
  inspectionId,
  stepKey,
  defectId,
  photos = [],
  disabled = false,
  multiple = true,
  maxPhotos = 10,
  mode = 'local',
}: PhotoFieldProps) {

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [localPreviews, setLocalPreviews] = useState<{ url: string; file: File }[]>([]);

  // S3 upload mode
  const { uploadPhoto, deletePhoto, isUploading } = mode === 'upload' && inspectionId
    ? usePhotoUpload(inspectionId)
    : { uploadPhoto: () => {}, deletePhoto: () => {}, isUploading: false };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    const currentCount = mode === 'upload' ? photos.length : localPreviews.length;

    // Check max photos limit
    if (currentCount + files.length > maxPhotos) {
      alert(`Maximum ${maxPhotos} photos allowed`);
      return;
    }

    if (mode === 'upload' && inspectionId && stepKey) {
      // Upload mode - send to S3
      for (const file of files) {
        await uploadPhoto({
          image: file,
          step_key: stepKey,
          defect_id: defectId,
        });
      }
    } else {
      // Local mode - create previews
      const newPreviews = files.map(file => ({
        url: URL.createObjectURL(file),
        file
      }));

      const updated = multiple
        ? [...localPreviews, ...newPreviews]
        : newPreviews;

      setLocalPreviews(updated);
      onChange?.(updated.map(p => p.file));
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleRemove = (index: number) => {
    if (mode === 'upload') {
      // Delete from S3
      const photo = photos[index];
      if (photo) {
        deletePhoto(photo.id);
      }
    } else {
      // Remove local preview
      const preview = localPreviews[index];
      URL.revokeObjectURL(preview.url);

      const updated = localPreviews.filter((_, i) => i !== index);
      setLocalPreviews(updated);
      onChange?.(updated.map(p => p.file));
    }
  };

  const displayPhotos = mode === 'upload'
    ? photos.map(p => ({ url: p.thumbnail_url || p.url, id: p.id }))
    : localPreviews;

  return (
    <div className="space-y-3">
      {/* Photo Grid */}
      {displayPhotos.length > 0 && (
        <div className="grid grid-cols-3 gap-3">
          {displayPhotos.map((photo, index) => (
            <div key={photo.id || index} className="relative group">
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
                  disabled={isUploading}
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Upload Button */}
      {!disabled && (multiple || displayPhotos.length === 0) && displayPhotos.length < maxPhotos && (
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,image/heic"
            capture="environment"  {/* Mobile camera */}
            multiple={multiple}
            onChange={handleFileSelect}
            className="hidden"
            id="photo-upload"
            disabled={isUploading}
          />
          <label
            htmlFor="photo-upload"
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border cursor-pointer transition-colors ${
              isUploading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
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
              {isUploading ? 'Uploading...' : displayPhotos.length > 0 ? 'Add More Photos' : 'Add Photos'}
            </span>
          </label>
          <p className="mt-1 text-xs" style={{ color: '#6b7280' }}>
            {displayPhotos.length}/{maxPhotos} photos
          </p>
        </div>
      )}
    </div>
  );
}
```

---

### 1.3 Testing Strategy for Photo Upload

#### 1.3.1 Backend Tests

**File:** `tests/test_photo_upload.py`
```python
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from apps.inspections.models import InspectionRun, InspectionPhoto
from apps.customers.models import Customer
from apps.assets.models import Vehicle


class PhotoUploadTest(TestCase):
    """Tests for photo upload functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.customer = Customer.objects.create(name="Test Customer")
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            vin="1HGCM82633A123456",
            unit_number="TRUCK-001"
        )

        self.inspection = InspectionRun.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            template_key='ansi_a92_2_2021_frequent_inspection',
            status='IN_PROGRESS',
            template_snapshot={'procedure': {'steps': []}, 'template': {}}
        )

    def create_test_image(self):
        """Create a test image file."""
        img = Image.new('RGB', (800, 600), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)

        return SimpleUploadedFile(
            name='test_photo.jpg',
            content=img_io.read(),
            content_type='image/jpeg'
        )

    def test_photo_upload(self):
        """Test uploading a photo to inspection."""
        image = self.create_test_image()

        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image
        )

        self.assertIsNotNone(photo.id)
        self.assertEqual(photo.step_key, 'visual_inspection')
        self.assertIsNotNone(photo.thumbnail)
        self.assertGreater(photo.file_size, 0)
        self.assertEqual(photo.width, 800)
        self.assertEqual(photo.height, 600)

    def test_thumbnail_generation(self):
        """Test automatic thumbnail generation."""
        image = self.create_test_image()

        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image
        )

        # Thumbnail should exist
        self.assertIsNotNone(photo.thumbnail)

        # Thumbnail should be smaller than original
        self.assertLess(photo.thumbnail.size, photo.image.size)

    def test_signed_url_generation(self):
        """Test signed URL generation for private photos."""
        image = self.create_test_image()

        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image
        )

        url = photo.get_signed_url()
        self.assertIsNotNone(url)
        self.assertIn('s3.amazonaws.com', url)  # S3 URL

    def test_cannot_upload_to_completed_inspection(self):
        """Test that photos cannot be uploaded to completed inspections."""
        self.inspection.status = 'COMPLETED'
        self.inspection.save()

        # This should be enforced at the API level
        # Model allows it, but views should block it
```

#### 1.3.2 Frontend Tests

**File:** `frontend/e2e/inspection-photo-upload.spec.ts`
```typescript
import { test, expect } from '@playwright/test';

test.describe('Inspection Photo Upload', () => {
  test('should upload photo during inspection', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="username"]', 'inspector1');
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');

    // Navigate to inspection
    await page.goto('/inspections');
    await page.click('a[href*="/inspections/"]');

    // Find photo upload button
    const uploadButton = page.locator('label[for="photo-upload"]');
    await expect(uploadButton).toBeVisible();

    // Upload photo
    const fileInput = page.locator('input#photo-upload');
    await fileInput.setInputFiles('e2e/fixtures/test-photo.jpg');

    // Wait for upload to complete
    await page.waitForResponse(resp =>
      resp.url().includes('/upload_photo/') && resp.status() === 201
    );

    // Verify photo appears
    const photoGrid = page.locator('.grid.grid-cols-3');
    await expect(photoGrid.locator('img')).toHaveCount(1);
  });

  test('should delete photo', async ({ page }) => {
    // ... similar setup ...

    // Hover over photo to reveal delete button
    const photoContainer = page.locator('.relative.group').first();
    await photoContainer.hover();

    // Click delete button
    const deleteButton = photoContainer.locator('button');
    await deleteButton.click();

    // Verify photo is removed
    await expect(page.locator('.grid.grid-cols-3 img')).toHaveCount(0);
  });
});
```

---

### 1.4 AWS S3 Setup

#### 1.4.1 Create S3 Bucket

```bash
# Using AWS CLI
aws s3api create-bucket \
  --bucket serviceprovider-inspections-prod \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket serviceprovider-inspections-prod \
  --versioning-configuration Status=Enabled

# Set lifecycle policy (delete thumbnails after 90 days)
aws s3api put-bucket-lifecycle-configuration \
  --bucket serviceprovider-inspections-prod \
  --lifecycle-configuration file://lifecycle-policy.json
```

**lifecycle-policy.json:**
```json
{
  "Rules": [
    {
      "Id": "DeleteOldThumbnails",
      "Status": "Enabled",
      "Prefix": "media/inspections/",
      "Filter": {
        "Prefix": "thumb_"
      },
      "Expiration": {
        "Days": 90
      }
    }
  ]
}
```

#### 1.4.2 Configure CORS

```bash
aws s3api put-bucket-cors \
  --bucket serviceprovider-inspections-prod \
  --cors-configuration file://cors-policy.json
```

**cors-policy.json:**
```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://yourdomain.com", "http://localhost:5173"],
      "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3600
    }
  ]
}
```

#### 1.4.3 Create IAM User for Django

```bash
# Create IAM user
aws iam create-user --user-name serviceprovider-django

# Attach policy
aws iam attach-user-policy \
  --user-name serviceprovider-django \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Create access keys
aws iam create-access-key --user-name serviceprovider-django
```

**Better: Create custom policy (least privilege):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::serviceprovider-inspections-prod",
        "arn:aws:s3:::serviceprovider-inspections-prod/*"
      ]
    }
  ]
}
```

#### 1.4.4 Setup CloudFront CDN (Optional but Recommended)

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name serviceprovider-inspections-prod.s3.amazonaws.com \
  --default-root-object index.html
```

**Benefits:**
- Faster global delivery
- HTTPS by default
- Reduced S3 costs (data transfer)
- Caching at edge locations

---

### 1.5 Phase 1 Deliverables

**Backend:**
- ✅ InspectionPhoto model with S3 storage
- ✅ Photo upload/delete API endpoints
- ✅ Automatic thumbnail generation
- ✅ Signed URL generation
- ✅ Integration with PDF export
- ✅ Integration with work orders
- ✅ 15+ tests for photo functionality

**Frontend:**
- ✅ Enhanced PhotoField component (local + S3 modes)
- ✅ Photo upload hook (usePhotoUpload)
- ✅ Photo API client
- ✅ Integration with inspection execution
- ✅ E2E tests for photo upload

**Infrastructure:**
- ✅ S3 bucket configuration
- ✅ CloudFront CDN setup
- ✅ IAM policies and credentials
- ✅ CORS configuration

**Documentation:**
- ✅ API documentation
- ✅ Setup guide for AWS
- ✅ Environment variables guide

---

## Phase 2: Frontend Inspection Execution UI

**Duration:** 1.5-2 weeks
**Priority:** P0 (Production blocking)

### 2.1 Current State Analysis

**Existing Components:**
- ✅ InspectionExecutePage.tsx (basic structure)
- ✅ InspectionStepper.tsx (step navigation)
- ✅ FieldRenderer.tsx (field types)
- ✅ StepRenderer.tsx (step display)
- ✅ AddDefectModal.tsx (defect capture)
- ✅ Various step types (SetupStep, VisualInspectionStep, etc.)

**Gaps:**
- ⚠️ Incomplete step-by-step navigation flow
- ⚠️ No progress persistence (save and resume)
- ⚠️ Limited mobile optimization
- ⚠️ No offline capability
- ⚠️ Photo integration needed

---

### 2.2 UI/UX Design

#### 2.2.1 Inspection Execution Flow

```
┌─────────────────────────────────────────────┐
│  INSPECTION EXECUTION                       │
├─────────────────────────────────────────────┤
│                                             │
│  [Progress Bar] ████████░░░░░░  Step 5/10  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Step 2: Boom Visual Inspection     │   │
│  │  ─────────────────────────────────  │   │
│  │                                     │   │
│  │  [Step Description]                 │   │
│  │  Inspect boom for cracks, dents...  │   │
│  │                                     │   │
│  │  Reference: ANSI A92.2 Section 8.2  │   │
│  │  "Inspect boom and platform for..." │   │
│  │                                     │   │
│  │  Assessment:                        │   │
│  │  ○ PASS  ○ FAIL  ○ N/A             │   │
│  │                                     │   │
│  │  [Photo Grid]                       │   │
│  │  [📷] [📷] [+Add Photos]            │   │
│  │                                     │   │
│  │  Notes:                             │   │
│  │  [Text area for inspector notes]    │   │
│  │                                     │   │
│  │  ✓ Add Defect                       │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [⬅ Previous]            [Next Step ➡]     │
│                                             │
│  [💾 Save Progress]   [📋 Review & Finish] │
│                                             │
└─────────────────────────────────────────────┘
```

#### 2.2.2 Mobile-First Design

**Key Principles:**
- Large touch targets (minimum 44x44px)
- Swipe gestures for next/previous step
- Camera integration for photos
- Offline mode with sync
- One-handed operation where possible

---

### 2.3 Implementation Plan

#### 2.3.1 Enhanced InspectionExecutePage

**File:** `frontend/src/features/inspections/InspectionExecutePage.tsx`

**Features to Add:**
1. **Progress Persistence**
   - Auto-save every 30 seconds
   - Save on step navigation
   - "Saved" indicator

2. **Step Navigation**
   - Previous/Next buttons
   - Jump to any step (from stepper)
   - Keyboard shortcuts (arrow keys)
   - Swipe gestures on mobile

3. **Progress Tracking**
   - Visual progress bar
   - Completed steps indicator
   - Required fields validation

4. **Photo Integration**
   - Direct camera access on mobile
   - Photo upload with S3
   - Photo count per step
   - Photo preview lightbox

5. **Defect Management**
   - Quick add defect button
   - Defect list per step
   - Visual severity indicators
   - Photo evidence attachment

6. **Offline Support** (Phase 2B)
   - Service worker for offline capability
   - Local storage cache
   - Sync when online
   - Conflict resolution

#### 2.3.2 Component Updates

**StepRenderer.tsx Enhancements:**
```typescript
interface StepRendererProps {
  step: Step;
  stepData: any;
  onFieldChange: (fieldKey: string, value: any) => void;
  onAddDefect: () => void;
  onPhotoUpload: (file: File) => void;
  photos: Photo[];
  defects: Defect[];
  inspectionId: string;
  isCompleted: boolean;
  standardText?: StandardTextReference;
}

export function StepRenderer({
  step,
  stepData,
  onFieldChange,
  onAddDefect,
  onPhotoUpload,
  photos,
  defects,
  inspectionId,
  isCompleted,
  standardText,
}: StepRendererProps) {
  return (
    <div className="space-y-6">
      {/* Step Header */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-xl font-semibold">{step.title}</h2>
        {step.description && (
          <p className="text-gray-600 mt-2">{step.description}</p>
        )}
      </div>

      {/* Standard Text Reference */}
      {standardText && (
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900">
                ANSI A92.2-2021 Section {standardText.section}
              </p>
              <p className="text-sm text-blue-700 mt-1">
                "{standardText.excerpt}"
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Fields */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
        {step.fields.map(field => (
          <FieldRenderer
            key={field.field_key}
            field={field}
            value={stepData[field.field_key]}
            onChange={(value) => onFieldChange(field.field_key, value)}
            disabled={isCompleted}
          />
        ))}
      </div>

      {/* Photos */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-medium mb-3">Photos ({photos.length})</h3>
        <PhotoField
          mode="upload"
          inspectionId={inspectionId}
          stepKey={step.step_key}
          photos={photos}
          disabled={isCompleted}
        />
      </div>

      {/* Defects */}
      {defects.length > 0 && (
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-3">Defects ({defects.length})</h3>
          <StepDefectsList defects={defects} />
        </div>
      )}

      {/* Add Defect Button */}
      {!isCompleted && (
        <button
          onClick={onAddDefect}
          className="w-full py-3 px-4 bg-red-50 text-red-700 border-2 border-red-200 rounded-lg font-medium hover:bg-red-100 transition-colors"
        >
          + Add Defect
        </button>
      )}
    </div>
  );
}
```

#### 2.3.3 Auto-Save Hook

**File:** `frontend/src/features/inspections/hooks/useAutoSave.ts`
```typescript
import { useEffect, useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import { inspectionsApi } from '@/api/inspections.api';
import { toast } from '@/components/ui/Toast';

export function useAutoSave(
  inspectionId: string,
  stepKey: string,
  stepData: any,
  enabled: boolean = true
) {
  const saveTimeoutRef = useRef<NodeJS.Timeout>();
  const lastSaveRef = useRef<string>('');

  const saveMutation = useMutation({
    mutationFn: () => inspectionsApi.saveStep(inspectionId, stepKey, stepData),
    onSuccess: () => {
      lastSaveRef.current = JSON.stringify(stepData);
      // Silent success (no toast)
    },
    onError: (error: any) => {
      toast.error('Failed to save progress');
      console.error('Auto-save error:', error);
    },
  });

  useEffect(() => {
    if (!enabled) return;

    // Check if data has changed
    const currentData = JSON.stringify(stepData);
    if (currentData === lastSaveRef.current) {
      return; // No changes
    }

    // Clear existing timeout
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Set new timeout for auto-save (30 seconds)
    saveTimeoutRef.current = setTimeout(() => {
      saveMutation.mutate();
    }, 30000); // 30 seconds

    // Cleanup
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [stepData, enabled]);

  return {
    isSaving: saveMutation.isPending,
    lastSaved: lastSaveRef.current,
    forceSave: () => saveMutation.mutate(),
  };
}
```

#### 2.3.4 Navigation Controls

**File:** `frontend/src/features/inspections/components/NavigationControls.tsx`
```typescript
interface NavigationControlsProps {
  currentStepIndex: number;
  totalSteps: number;
  onPrevious: () => void;
  onNext: () => void;
  onSave: () => void;
  onReview: () => void;
  isSaving: boolean;
  canGoNext: boolean;
  canGoPrevious: boolean;
}

export function NavigationControls({
  currentStepIndex,
  totalSteps,
  onPrevious,
  onNext,
  onSave,
  onReview,
  isSaving,
  canGoNext,
  canGoPrevious,
}: NavigationControlsProps) {
  const isLastStep = currentStepIndex === totalSteps - 1;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 md:relative md:border-0 md:mt-6">
      <div className="flex items-center justify-between gap-4">
        {/* Previous Button */}
        <button
          onClick={onPrevious}
          disabled={!canGoPrevious}
          className="flex items-center gap-2 px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="hidden sm:inline">Previous</span>
        </button>

        {/* Progress Indicator */}
        <div className="text-sm text-gray-600 font-medium">
          Step {currentStepIndex + 1} of {totalSteps}
        </div>

        {/* Next/Review Button */}
        <button
          onClick={isLastStep ? onReview : onNext}
          disabled={!canGoNext}
          className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>{isLastStep ? 'Review & Finish' : 'Next Step'}</span>
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isLastStep ? "M9 5l7 7-7 7" : "M9 5l7 7-7 7"} />
          </svg>
        </button>
      </div>

      {/* Save Status */}
      <div className="mt-3 text-center">
        <button
          onClick={onSave}
          disabled={isSaving}
          className="text-sm text-gray-600 hover:text-gray-900 flex items-center justify-center gap-2 mx-auto"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
          </svg>
          <span>{isSaving ? 'Saving...' : 'Save Progress'}</span>
        </button>
      </div>
    </div>
  );
}
```

---

### 2.4 Mobile Optimization

#### 2.4.1 Touch Gestures

**File:** `frontend/src/features/inspections/hooks/useSwipeGesture.ts`
```typescript
import { useEffect, useRef } from 'react';

interface SwipeHandlers {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
}

export function useSwipeGesture({ onSwipeLeft, onSwipeRight }: SwipeHandlers) {
  const touchStartX = useRef<number>(0);
  const touchEndX = useRef<number>(0);

  useEffect(() => {
    const handleTouchStart = (e: TouchEvent) => {
      touchStartX.current = e.touches[0].clientX;
    };

    const handleTouchEnd = (e: TouchEvent) => {
      touchEndX.current = e.changedTouches[0].clientX;
      handleSwipe();
    };

    const handleSwipe = () => {
      const swipeThreshold = 50; // minimum swipe distance
      const diff = touchStartX.current - touchEndX.current;

      if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
          // Swipe left (next)
          onSwipeLeft?.();
        } else {
          // Swipe right (previous)
          onSwipeRight?.();
        }
      }
    };

    document.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchend', handleTouchEnd);

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, [onSwipeLeft, onSwipeRight]);
}
```

#### 2.4.2 Camera Integration

```typescript
// Enhanced PhotoField with camera capture
<input
  type="file"
  accept="image/*"
  capture="environment"  // Use rear camera on mobile
  onChange={handlePhotoCapture}
/>
```

---

### 2.5 Phase 2 Deliverables

**UI Components:**
- ✅ Enhanced InspectionExecutePage
- ✅ StepRenderer with full features
- ✅ NavigationControls component
- ✅ Progress tracking component
- ✅ Auto-save functionality
- ✅ Swipe gesture support
- ✅ Mobile-optimized layout

**Features:**
- ✅ Step-by-step navigation
- ✅ Progress persistence (auto-save)
- ✅ Photo upload integration
- ✅ Defect capture per step
- ✅ Standard text display
- ✅ Mobile camera support
- ✅ Keyboard shortcuts
- ✅ Touch gestures

**Testing:**
- ✅ E2E tests for full inspection flow
- ✅ Mobile responsiveness tests
- ✅ Touch gesture tests
- ✅ Photo upload integration tests
- ✅ Auto-save behavior tests

---

## Testing Strategy

### 3.1 Backend Tests

**Coverage Target:** 95%

**Test Files:**
- `tests/test_photo_upload.py` (20 tests)
- `tests/test_photo_model.py` (15 tests)
- `tests/test_photo_api.py` (25 tests)
- `tests/test_pdf_with_photos.py` (10 tests)

### 3.2 Frontend Tests

**E2E Tests (Playwright):**
- Complete inspection flow with photos
- Photo upload/delete
- Mobile camera capture
- Auto-save functionality
- Offline mode (Phase 2B)
- Swipe gestures

**Component Tests:**
- PhotoField component (local + S3 modes)
- StepRenderer with photos
- NavigationControls
- Auto-save hook

---

## Deployment Plan

### 4.1 Phase 1 Deployment (Photo Upload)

**Week 1:**
- Day 1-2: Backend implementation
- Day 3-4: Frontend implementation
- Day 5: Integration testing
- Day 6-7: AWS setup and testing

**Week 2:**
- Day 1-3: Bug fixes and polish
- Day 4: Staging deployment
- Day 5: User acceptance testing
- Day 6-7: Production deployment

### 4.2 Phase 2 Deployment (Inspection UI)

**Week 3:**
- Day 1-2: UI components
- Day 3-4: Mobile optimization
- Day 5: Integration testing
- Day 6-7: E2E tests

**Week 4:**
- Day 1-3: Bug fixes and polish
- Day 4: Staging deployment
- Day 5: User acceptance testing
- Day 6-7: Production deployment

---

## Success Metrics

### 5.1 Photo Upload Metrics

- ✅ Photo upload success rate > 99%
- ✅ Average upload time < 3 seconds
- ✅ Thumbnail generation time < 1 second
- ✅ S3 storage cost < $50/month (first 1000 inspections)
- ✅ Zero data loss incidents

### 5.2 Inspection UI Metrics

- ✅ Inspection completion time reduced by 30%
- ✅ Mobile usage > 60% of inspections
- ✅ Auto-save success rate > 99%
- ✅ User satisfaction score > 4.5/5
- ✅ Photo capture rate > 80% of inspections

---

## Risk Mitigation

### 6.1 Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| S3 upload failures | High | Low | Retry logic, error handling, fallback to local storage |
| Large photo file sizes | Medium | Medium | Client-side compression, file size limits |
| Mobile browser compatibility | Medium | Low | Progressive enhancement, feature detection |
| Offline mode complexity | High | Medium | Phase 2B (optional), service worker |
| AWS cost overruns | Medium | Low | CloudFront caching, lifecycle policies, monitoring |

### 6.2 User Adoption Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Resistance to photo requirements | High | Make photos optional except for critical defects |
| Learning curve for mobile UI | Medium | In-app tutorials, tooltips, training videos |
| Poor mobile network | High | Offline mode (Phase 2B), compression, resume uploads |

---

## Budget Estimate

### 7.1 AWS Costs (Monthly)

**S3 Storage:**
- 1000 inspections/month × 5 photos avg × 2MB avg = 10GB
- 10GB × $0.023/GB = $0.23/month

**S3 Requests:**
- Uploads: 5000 photos × $0.005/1000 = $0.025
- Downloads: 10000 views × $0.0004/1000 = $0.004

**CloudFront:**
- 50GB data transfer × $0.085/GB = $4.25/month

**Total Monthly Cost:** ~$5/month (first 1000 inspections)

**At Scale (10,000 inspections/month):**
- Storage: 100GB × $0.023 = $2.30
- Requests: $0.50
- CloudFront: $42.50
- **Total: ~$50/month**

### 7.2 Development Costs

- Backend development: 1 week × 1 developer
- Frontend development: 1.5 weeks × 1 developer
- Testing & QA: 0.5 weeks × 1 QA engineer
- **Total: 3 weeks of effort**

---

## Next Steps

### Immediate Actions (Week 1)

1. **Set up AWS S3 bucket** (Day 1)
   - Create bucket
   - Configure CORS
   - Set up IAM user
   - Test uploads

2. **Backend implementation** (Day 2-3)
   - Install dependencies
   - Create InspectionPhoto model
   - Implement API endpoints
   - Write tests

3. **Frontend implementation** (Day 4-5)
   - Update PhotoField component
   - Create photo upload hook
   - Integrate with inspection UI
   - Write E2E tests

4. **Integration testing** (Day 6-7)
   - End-to-end testing
   - Performance testing
   - Mobile testing
   - Bug fixes

### Sign-off Required

Before proceeding, please confirm:
- [ ] AWS account and credentials ready
- [ ] Budget approved (~$50/month at scale)
- [ ] Development timeline accepted (3-4 weeks)
- [ ] Success metrics agreed upon

---

**Document Version:** 1.0
**Last Updated:** 2026-03-16
**Status:** Ready for Review

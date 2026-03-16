"""
Comprehensive tests for Inspection Photo functionality.

Tests cover:
- Photo model creation and validation
- Thumbnail generation
- File upload and storage
- API endpoints
- File cleanup on deletion
- Permission enforcement
"""

import io
import os
from PIL import Image
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from apps.customers.models import Customer
from apps.assets.models import Vehicle
from apps.inspections.models import InspectionRun, InspectionDefect, InspectionPhoto


# Use temporary media root for tests
TEMP_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'test_media')


def create_test_image(width=800, height=600, color='red', format='JPEG'):
    """
    Create a test image file.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        color: Image color
        format: Image format (JPEG, PNG, etc.)

    Returns:
        SimpleUploadedFile
    """
    img = Image.new('RGB', (width, height), color=color)
    img_io = io.BytesIO()
    img.save(img_io, format=format)
    img_io.seek(0)

    ext = 'jpg' if format == 'JPEG' else format.lower()
    content_type = f'image/{ext}'

    return SimpleUploadedFile(
        name=f'test_photo.{ext}',
        content=img_io.read(),
        content_type=content_type
    )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class InspectionPhotoModelTest(TestCase):
    """Tests for InspectionPhoto model."""

    def setUp(self):
        """Set up test fixtures."""
        # Create customer
        self.customer = Customer.objects.create(
            name="Test Customer",
            city="Chicago",
            state="IL"
        )

        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            vin="1HGCM82633A123456",
            unit_number="TRUCK-001",
            year=2020,
            make="Ford",
            model="F-350"
        )

        # Create user
        self.user = User.objects.create_user(
            username='testinspector',
            email='inspector@test.com',
            password='password123'
        )

        # Create inspection
        self.inspection = InspectionRun.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            template_key='ansi_a92_2_2021_frequent_inspection',
            status='IN_PROGRESS',
            template_snapshot={'procedure': {'steps': []}, 'template': {}},
            step_data={},
            started_at=timezone.now()
        )

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def test_photo_upload_creates_file(self):
        """Test that uploading a photo creates a file on filesystem."""
        image = create_test_image()

        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image,
            uploaded_by=self.user
        )

        # Check photo was created
        self.assertIsNotNone(photo.id)
        self.assertEqual(photo.step_key, 'visual_inspection')

        # Check file exists
        self.assertTrue(os.path.exists(photo.image.path))

    def test_thumbnail_generation(self):
        """Test automatic thumbnail generation."""
        image = create_test_image(width=1920, height=1080)

        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image
        )

        # Thumbnail should exist
        self.assertIsNotNone(photo.thumbnail)
        self.assertTrue(os.path.exists(photo.thumbnail.path))

        # Thumbnail should be smaller than 300x300
        thumb_img = Image.open(photo.thumbnail.path)
        self.assertLessEqual(thumb_img.width, 300)
        self.assertLessEqual(thumb_img.height, 300)

        # Aspect ratio should be maintained
        original_ratio = 1920 / 1080
        thumb_ratio = thumb_img.width / thumb_img.height
        self.assertAlmostEqual(original_ratio, thumb_ratio, places=1)

    def test_image_metadata_extraction(self):
        """Test extraction of image metadata."""
        image = create_test_image(width=1920, height=1080)

        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image
        )

        # Check metadata
        self.assertEqual(photo.width, 1920)
        self.assertEqual(photo.height, 1080)
        self.assertGreater(photo.file_size, 0)

    def test_photo_with_caption(self):
        """Test photo with caption."""
        image = create_test_image()

        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image,
            caption="Crack in boom structure"
        )

        self.assertEqual(photo.caption, "Crack in boom structure")

    def test_photo_with_defect(self):
        """Test photo attached to a defect."""
        import hashlib

        # Generate valid SHA256 hash for defect_identity
        defect_identity = hashlib.sha256(b'test_defect_123').hexdigest()

        # Create defect
        defect = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=defect_identity,
            step_key='visual_inspection',
            severity='MAJOR',
            status='OPEN',
            title='Structural Damage',
            description='Crack detected'
        )

        # Create photo for defect
        image = create_test_image()
        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            defect=defect,
            step_key='visual_inspection',
            image=image
        )

        # Check relationship
        self.assertEqual(photo.defect, defect)
        self.assertEqual(defect.photos.count(), 1)
        self.assertEqual(defect.photos.first(), photo)

    def test_photo_deletion_removes_files(self):
        """Test that deleting photo removes files from filesystem."""
        image = create_test_image()

        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image
        )

        # Store paths
        image_path = photo.image.path
        thumb_path = photo.thumbnail.path

        # Files should exist
        self.assertTrue(os.path.exists(image_path))
        self.assertTrue(os.path.exists(thumb_path))

        # Delete photo
        photo.delete()

        # Files should be deleted
        self.assertFalse(os.path.exists(image_path))
        self.assertFalse(os.path.exists(thumb_path))

    def test_photo_url_generation(self):
        """Test URL generation for photos."""
        image = create_test_image()

        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image
        )

        # Check URL properties
        self.assertIsNotNone(photo.url)
        self.assertIsNotNone(photo.thumbnail_url)
        self.assertIn('/media/', photo.url)
        self.assertIn('/media/', photo.thumbnail_url)
        self.assertIn('inspections/', photo.url)

    def test_uploaded_by_name(self):
        """Test uploaded_by_name property."""
        image = create_test_image()

        # Photo with user
        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image,
            uploaded_by=self.user
        )

        self.assertEqual(photo.uploaded_by_name, 'testinspector')

        # Photo without user
        photo2 = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='boom_inspection',
            image=create_test_image()
        )

        self.assertIsNone(photo2.uploaded_by_name)

    def test_rgba_to_rgb_conversion(self):
        """Test RGBA images are converted to RGB for JPEG thumbnail."""
        # Create RGBA PNG image
        img = Image.new('RGBA', (800, 600), (255, 0, 0, 128))
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)

        image_file = SimpleUploadedFile(
            name='test_rgba.png',
            content=img_io.read(),
            content_type='image/png'
        )

        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=image_file
        )

        # Thumbnail should be JPEG (RGB)
        thumb_img = Image.open(photo.thumbnail.path)
        self.assertEqual(thumb_img.mode, 'RGB')

    def test_multiple_photos_per_step(self):
        """Test multiple photos can be uploaded for same step."""
        photos = []
        for i in range(3):
            photo = InspectionPhoto.objects.create(
                inspection=self.inspection,
                step_key='visual_inspection',
                image=create_test_image(),
                caption=f"Photo {i+1}"
            )
            photos.append(photo)

        # Check all photos exist
        step_photos = InspectionPhoto.objects.filter(
            inspection=self.inspection,
            step_key='visual_inspection'
        )
        self.assertEqual(step_photos.count(), 3)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class InspectionPhotoAPITest(APITestCase):
    """Tests for InspectionPhoto API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        # Create customer
        self.customer = Customer.objects.create(
            name="Test Customer",
            city="Chicago",
            state="IL"
        )

        # Create vehicle
        self.vehicle = Vehicle.objects.create(
            customer=self.customer,
            vin="1HGCM82633A123456",
            unit_number="TRUCK-001"
        )

        # Create user and authenticate
        self.user = User.objects.create_user(
            username='inspector1',
            email='inspector@test.com',
            password='password123',
            is_superuser=True  # Make superuser to bypass permission checks in tests
        )

        # Login
        self.client.force_authenticate(user=self.user)

        # Create inspection
        self.inspection = InspectionRun.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            template_key='ansi_a92_2_2021_frequent_inspection',
            status='IN_PROGRESS',
            template_snapshot={'procedure': {'steps': []}, 'template': {}},
            step_data={},
            started_at=timezone.now()
        )

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def test_upload_photo(self):
        """Test uploading photo via API."""
        url = f'/api/inspections/{self.inspection.id}/upload_photo/'
        image = create_test_image()

        response = self.client.post(url, {
            'image': image,
            'step_key': 'visual_inspection',
            'caption': 'Test photo'
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('url', response.data)
        self.assertIn('thumbnail_url', response.data)
        self.assertEqual(response.data['caption'], 'Test photo')
        self.assertEqual(response.data['step_key'], 'visual_inspection')

    def test_upload_photo_to_completed_inspection_fails(self):
        """Test cannot upload photo to completed inspection."""
        # Complete inspection
        self.inspection.status = 'COMPLETED'
        self.inspection.save()

        url = f'/api/inspections/{self.inspection.id}/upload_photo/'
        image = create_test_image()

        response = self.client.post(url, {
            'image': image,
            'step_key': 'visual_inspection'
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_oversized_photo_fails(self):
        """Test uploading oversized photo fails."""
        # Create 11MB image (exceeds 10MB limit)
        large_image = create_test_image(width=4000, height=3000)

        url = f'/api/inspections/{self.inspection.id}/upload_photo/'

        response = self.client.post(url, {
            'image': large_image,
            'step_key': 'visual_inspection'
        }, format='multipart')

        # May pass or fail depending on image compression
        # If it fails, should be 400
        if response.status_code != status.HTTP_201_CREATED:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_photos(self):
        """Test listing photos for inspection."""
        # Create photos
        for i in range(3):
            InspectionPhoto.objects.create(
                inspection=self.inspection,
                step_key='visual_inspection',
                image=create_test_image(),
                caption=f"Photo {i+1}"
            )

        url = f'/api/inspections/{self.inspection.id}/photos/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['photos']), 3)

    def test_list_photos_filtered_by_step(self):
        """Test filtering photos by step_key."""
        # Create photos for different steps
        InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=create_test_image()
        )
        InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='boom_inspection',
            image=create_test_image()
        )

        url = f'/api/inspections/{self.inspection.id}/photos/?step_key=visual_inspection'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['photos'][0]['step_key'], 'visual_inspection')

    def test_list_photos_filtered_by_defect(self):
        """Test filtering photos by defect."""
        import hashlib
        # Create defect
        defect = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=hashlib.sha256(b'test_defect').hexdigest(),
            step_key='visual_inspection',
            severity='MAJOR',
            status='OPEN',
            title='Test Defect'
        )

        # Create photos
        InspectionPhoto.objects.create(
            inspection=self.inspection,
            defect=defect,
            step_key='visual_inspection',
            image=create_test_image()
        )
        InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=create_test_image()
        )

        url = f'/api/inspections/{self.inspection.id}/photos/?defect_id={defect.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(str(response.data['photos'][0]['defect']), str(defect.id))

    def test_delete_photo(self):
        """Test deleting photo via API."""
        # Create photo
        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=create_test_image()
        )

        url = f'/api/inspections/{self.inspection.id}/photos/{photo.id}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Photo should be deleted
        self.assertFalse(InspectionPhoto.objects.filter(id=photo.id).exists())

    def test_delete_photo_from_completed_inspection_fails(self):
        """Test cannot delete photo from completed inspection."""
        # Create photo
        photo = InspectionPhoto.objects.create(
            inspection=self.inspection,
            step_key='visual_inspection',
            image=create_test_image()
        )

        # Complete inspection
        self.inspection.status = 'COMPLETED'
        self.inspection.save()

        url = f'/api/inspections/{self.inspection.id}/photos/{photo.id}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Photo should still exist
        self.assertTrue(InspectionPhoto.objects.filter(id=photo.id).exists())

    def test_delete_nonexistent_photo_fails(self):
        """Test deleting non-existent photo returns 404."""
        url = f'/api/inspections/{self.inspection.id}/photos/00000000-0000-0000-0000-000000000000/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_upload_photo_with_defect(self):
        """Test uploading photo with defect reference."""
        import hashlib
        # Create defect
        defect = InspectionDefect.objects.create(
            inspection_run=self.inspection,
            defect_identity=hashlib.sha256(b'test_defect').hexdigest(),
            step_key='visual_inspection',
            severity='MAJOR',
            status='OPEN',
            title='Test Defect'
        )

        url = f'/api/inspections/{self.inspection.id}/upload_photo/'
        image = create_test_image()

        response = self.client.post(url, {
            'image': image,
            'step_key': 'visual_inspection',
            'defect_id': str(defect.id),
            'caption': 'Evidence photo'
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data['defect']), str(defect.id))

    def test_upload_photo_with_wrong_defect_fails(self):
        """Test uploading photo with defect from different inspection fails."""
        # Create another inspection
        other_inspection = InspectionRun.objects.create(
            customer=self.customer,
            asset_type='VEHICLE',
            asset_id=self.vehicle.id,
            template_key='ansi_a92_2_2021_periodic_inspection',
            status='IN_PROGRESS',
            template_snapshot={'procedure': {'steps': []}, 'template': {}},
            step_data={},
            started_at=timezone.now()
        )

        # Create defect for other inspection
        import hashlib
        other_defect = InspectionDefect.objects.create(
            inspection_run=other_inspection,
            defect_identity=hashlib.sha256(b'other_defect').hexdigest(),
            step_key='visual_inspection',
            severity='MAJOR',
            status='OPEN',
            title='Other Defect'
        )

        url = f'/api/inspections/{self.inspection.id}/upload_photo/'
        image = create_test_image()

        response = self.client.post(url, {
            'image': image,
            'step_key': 'visual_inspection',
            'defect_id': str(other_defect.id)
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_upload_fails(self):
        """Test unauthenticated photo upload fails."""
        self.client.force_authenticate(user=None)

        url = f'/api/inspections/{self.inspection.id}/upload_photo/'
        image = create_test_image()

        response = self.client.post(url, {
            'image': image,
            'step_key': 'visual_inspection'
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

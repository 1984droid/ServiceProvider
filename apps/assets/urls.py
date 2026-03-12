"""
URL routing for Asset Management API

Provides router configuration for DRF ViewSets
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import VehicleViewSet, EquipmentViewSet, VINDecodeDataViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'vin-decode-data', VINDecodeDataViewSet, basename='vindecodedata')

urlpatterns = [
    path('', include(router.urls)),
]

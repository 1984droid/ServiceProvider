"""
URL configuration for inspections app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet, InspectionRunViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'inspections', InspectionRunViewSet, basename='inspection')

app_name = 'inspections'

urlpatterns = [
    path('', include(router.urls)),
]

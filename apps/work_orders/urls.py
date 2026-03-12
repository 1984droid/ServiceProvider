"""
Work Orders URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.work_orders.views import (
    WorkOrderViewSet,
    WorkOrderLineViewSet,
    VocabularyViewSet,
)

router = DefaultRouter()
router.register(r'work-orders', WorkOrderViewSet, basename='workorder')
router.register(r'work-order-lines', WorkOrderLineViewSet, basename='workorderline')
router.register(r'vocabulary', VocabularyViewSet, basename='vocabulary')

urlpatterns = [
    path('', include(router.urls)),
]

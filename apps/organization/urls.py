"""URL configuration for organization app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DepartmentViewSet, EmployeeViewSet

router = DefaultRouter()
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
]

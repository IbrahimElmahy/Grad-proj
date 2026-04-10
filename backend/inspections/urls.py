from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import InspectionViewSet, UploadInspectionView

router = DefaultRouter()
router.register(r'inspections', InspectionViewSet)

urlpatterns = [
    path('api/upload/', UploadInspectionView.as_view(), name='api_upload_inspection'),
    path('api/', include(router.urls)),
]

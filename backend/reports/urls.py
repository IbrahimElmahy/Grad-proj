from django.urls import path
from .views import ExportInspectionsView

urlpatterns = [
    path('export/', ExportInspectionsView.as_view(), name='export-inspections'),
]

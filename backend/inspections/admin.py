from django.contrib import admin
from .models import Inspection, InspectionImage, DetectedObject

class DetectedObjectInline(admin.TabularInline):
    model = DetectedObject
    extra = 0

class InspectionImageInline(admin.StackedInline):
    model = InspectionImage
    extra = 0
    inlines = [DetectedObjectInline] # Note: Nested inlines are not directly supported in Django Admin without 3rd party, so we'll flatten it.

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'camera_id', 'timestamp', 'status', 'risk_level')
    list_filter = ('status', 'risk_level', 'timestamp')
    search_fields = ('camera_id', 'id')
    inlines = [InspectionImageInline]

@admin.register(InspectionImage)
class InspectionImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'inspection', 'created_at')

@admin.register(DetectedObject)
class DetectedObjectAdmin(admin.ModelAdmin):
    list_display = ('object_type', 'severity', 'confidence', 'image')
    list_filter = ('object_type', 'severity')

from django.shortcuts import render, get_object_or_404, redirect
from inspections.models import Inspection, DetectedObject, RiskLevel

def upload(request):
    return render(request, 'dashboard/upload.html')

def index(request):
    inspections_count = Inspection.objects.count()
    risks_detected = DetectedObject.objects.exclude(severity=RiskLevel.SAFE).count()
    
    recent_inspections = Inspection.objects.all()[:5]

    context = {
        'status': 'System Online',
        'inspections_count': inspections_count,
        'risks_detected': risks_detected,
        'recent_inspections': recent_inspections,
    }
    return render(request, 'dashboard/index.html', context)

def inspection_list(request):
    inspections = Inspection.objects.all()
    context = {
        'inspections': inspections
    }
    return render(request, 'dashboard/inspection_list.html', context)

def inspection_detail(request, pk):
    inspection = get_object_or_404(Inspection, pk=pk)
    # Get all detected objects across all images for this inspection
    detected_objects = []
    for img in inspection.images.all():
        detected_objects.extend(img.detected_objects.all())

    context = {
        'inspection': inspection,
        'detected_objects': detected_objects
    }
    return render(request, 'dashboard/inspection_detail.html', context)

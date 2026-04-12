from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from inspections.models import Inspection, RiskLevel
from django.db.models import Count, Q
import datetime
from django.utils import timezone

def dashboard_view(request):
    # Context Data for Template
    total = Inspection.objects.count()
    risks = Inspection.objects.exclude(risk_level=RiskLevel.SAFE).count()
    
    # Simple status determination
    alert_exists = Inspection.objects.filter(status='ALERT', timestamp__date=timezone.now().date()).exists()
    status_text = "Runway Safe"
    if alert_exists:
        status_text = "Hazards Detected"

    context = {
        'inspections_count': total,
        'risks_detected': risks,
        'status': status_text
    }
    return render(request, 'dashboard/index.html', context)

def upload_view(request):
    return render(request, 'dashboard/upload.html')

def inspection_list_view(request):
    inspections = Inspection.objects.all().order_by('-timestamp')
    return render(request, 'dashboard/inspection_list.html', {'inspections': inspections})

def inspection_detail_view(request, pk):
    inspection = Inspection.objects.get(pk=pk)
    # Get all objects detected in this inspection's images
    detected_objects = []
    for img in inspection.images.all():
        detected_objects.extend(img.detected_objects.all())
        
    return render(request, 'dashboard/inspection_detail.html', {
        'inspection': inspection, 
        'detected_objects': detected_objects
    })

def reports_view(request):
    return render(request, 'dashboard/reports.html')

class DashboardStatsView(APIView):
    def get(self, request):
        today = timezone.now().date()
        week_start = today - datetime.timedelta(days=7)
        
        total_inspections = Inspection.objects.count()
        today_inspections = Inspection.objects.filter(timestamp__date=today).count()
        week_inspections = Inspection.objects.filter(timestamp__date__gte=week_start).count()
        
        alerts_today = Inspection.objects.filter(
            timestamp__date=today, 
            status='ALERT'
        ).count()
        
        risk_distribution = Inspection.objects.values('risk_level').annotate(count=Count('id'))
        
        # Recent Alerts
        recent_alerts = Inspection.objects.filter(status='ALERT').order_by('-timestamp')[:5]
        alerts_data = [{
            'id': str(a.id),
            'time': a.timestamp.strftime('%H:%M'),
            'risk': a.risk_level,
            'camera': a.camera_id
        } for a in recent_alerts]

        return Response({
            'total_inspections': total_inspections,
            'today_inspections': today_inspections,
            'week_inspections': week_inspections,
            'alerts_today': alerts_today,
            'risk_distribution': risk_distribution,
            'recent_alerts': alerts_data
        })

import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from inspections.models import Inspection

class ExportInspectionsView(APIView):
    def get(self, request):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="inspections_report.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['ID', 'Date', 'Time', 'Camera ID', 'Status', 'Risk Level', 'Image URL'])

        inspections = Inspection.objects.all().order_by('-timestamp')
        
        # Optional: Date filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            inspections = inspections.filter(timestamp__date__gte=start_date)
        if end_date:
            inspections = inspections.filter(timestamp__date__lte=end_date)

        for ins in inspections:
            # Get main image url if exists (handling None)
            img_url = ""
            first_image = ins.images.first()
            if first_image and first_image.image:
                img_url = first_image.image.url

            writer.writerow([
                str(ins.id),
                ins.timestamp.strftime('%Y-%m-%d'),
                ins.timestamp.strftime('%H:%M:%S'),
                ins.camera_id,
                ins.get_status_display(),
                ins.get_risk_level_display(),
                img_url
            ])

        return response

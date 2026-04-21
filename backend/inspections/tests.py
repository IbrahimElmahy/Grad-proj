import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import DetectedObject, Inspection, ObjectType, RiskLevel


class UploadInspectionViewTests(APITestCase):
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    @patch('inspections.api_views.GeminiAdvisor')
    @patch('inspections.api_views.YoloDetector')
    def test_image_upload_persists_structured_detection_log(self, detector_cls, advisor_cls):
        detector = detector_cls.return_value
        detector.detect.return_value = [
            {
                'label': 'Debris',
                'confidence': 0.93,
                'severity': 'High',
                'detected_at_utc': '2026-04-08T11:22:33.456Z',
                'frame_index': 0,
                'frame_timestamp_seconds': None,
                'bbox': {
                    'x': 12,
                    'y': 24,
                    'w': 60,
                    'h': 48,
                    'x1': 12,
                    'y1': 24,
                    'x2': 72,
                    'y2': 72,
                },
            }
        ]

        advisor = advisor_cls.return_value
        advisor.model = None

        response = self.client.post(
            reverse('api_upload_inspection'),
            {
                'camera_id': 'CAM-01',
                'image': SimpleUploadedFile('frame.jpg', b'fake-image-bytes', content_type='image/jpeg'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, 201)

        inspection = Inspection.objects.get()
        detected_object = DetectedObject.objects.get()

        self.assertEqual(inspection.risk_level, RiskLevel.HIGH)
        self.assertEqual(inspection.status, Inspection.Status.ALERT)
        self.assertEqual(inspection.analysis_log['total_detections'], 1)
        self.assertEqual(inspection.analysis_log['highest_severity'], RiskLevel.HIGH)
        self.assertEqual(inspection.analysis_log['detections'][0]['bbox_xywh']['x'], 12)

        self.assertEqual(detected_object.raw_label, 'Debris')
        self.assertEqual(detected_object.object_type, ObjectType.DEBRIS)
        self.assertEqual(detected_object.severity, RiskLevel.HIGH)
        self.assertEqual(detected_object.bbox_x, 12)
        self.assertEqual(detected_object.bbox_y, 24)
        self.assertEqual(detected_object.bbox_w, 60)
        self.assertEqual(detected_object.bbox_h, 48)
        self.assertEqual(detected_object.bbox_x1, 12)
        self.assertEqual(detected_object.bbox_y1, 24)
        self.assertEqual(detected_object.bbox_x2, 72)
        self.assertEqual(detected_object.bbox_y2, 72)

        self.assertEqual(response.data['analysis_log']['inspection_risk_level'], RiskLevel.HIGH)
        self.assertEqual(response.data['images'][0]['detected_objects'][0]['bbox_xywh']['w'], 60)

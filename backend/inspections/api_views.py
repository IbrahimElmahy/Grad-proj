import datetime
import os

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .hazard_utils import (
    build_analysis_log,
    build_detection_log_entry,
    classify_detection_label,
    fallback_suggestion,
    highest_risk_level,
    is_alert_level,
    utc_now_iso,
)
from .models import DetectedObject, Inspection, InspectionImage, RiskLevel, ObjectType
from .realtime import broadcast_inspection_alert
from .serializers import InspectionSerializer

GeminiAdvisor = None
YoloDetector = None


def _get_gemini_advisor_class():
    global GeminiAdvisor
    if GeminiAdvisor is None:
        from ai_engine.gemini_service import GeminiAdvisor as ImportedGeminiAdvisor

        GeminiAdvisor = ImportedGeminiAdvisor
    return GeminiAdvisor


def _get_yolo_detector_class():
    global YoloDetector
    if YoloDetector is None:
        from ai_engine.yolo_service import YoloDetector as ImportedYoloDetector

        YoloDetector = ImportedYoloDetector
    return YoloDetector


def _coerce_int(value):
    if value is None:
        return None
    return int(round(float(value)))


def _parse_detected_at(value):
    if not value:
        return timezone.now()

    parsed = parse_datetime(value)
    if parsed is not None:
        return parsed

    try:
        return datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return timezone.now()


def _generate_suggestion(advisor, object_type, severity):
    fallback = fallback_suggestion(object_type, severity)
    if severity not in {RiskLevel.HIGH, RiskLevel.MEDIUM}:
        return fallback

    if not advisor or not getattr(advisor, 'model', None):
        return fallback

    suggestion = advisor.generate_solution(object_type=object_type, severity=severity)
    if suggestion and not suggestion.startswith('Error'):
        return suggestion
    return fallback


class InspectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows inspections to be viewed.
    """

    queryset = Inspection.objects.all().prefetch_related('images__detected_objects').order_by('-timestamp')
    serializer_class = InspectionSerializer


class UploadInspectionView(APIView):
    """
    API endpoint for cameras/mobile to upload inspection images.
    Triggers AI analysis automatically and stores a structured JSON log.
    """

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        camera_id = request.data.get('camera_id', 'Unknown Camera')
        image_file = request.data.get('image')
        video_file = request.data.get('video')

        if not image_file and not video_file:
            return Response({'error': 'No image or video provided'}, status=status.HTTP_400_BAD_REQUEST)

        inspection = Inspection.objects.create(
            camera_id=camera_id,
            status=Inspection.Status.PROCESSING,
            risk_level=RiskLevel.SAFE,
        )

        detector = None
        detector_error = None
        detections = []

        try:
            detector = _get_yolo_detector_class()()
        except Exception as exc:
            detector_error = str(exc)
            print(f"Failed to load YOLO model: {exc}")

        if video_file:
            inspection.video = video_file
            inspection.save()

            if detector:
                try:
                    today = timezone.now().date()
                    date_path = today.strftime('%Y/%m/%d')
                    frames_rel_path = f"inspections/processed/{date_path}/{inspection.id}"
                    output_dir_base = os.path.join(settings.MEDIA_ROOT, frames_rel_path)

                    video_filename = os.path.basename(inspection.video.path)
                    rel_processed_video_path = f"inspections/processed_videos/{date_path}/{inspection.id}_{video_filename}"
                    full_processed_video_path = os.path.join(settings.MEDIA_ROOT, rel_processed_video_path)

                    frame_results, out_vid_path = detector.detect_video(
                        video_path=inspection.video.path,
                        output_dir_base=output_dir_base,
                        output_video_path=full_processed_video_path,
                    )

                    if out_vid_path and os.path.exists(out_vid_path):
                        inspection.processed_video = rel_processed_video_path
                        inspection.save(update_fields=['processed_video'])

                    for frame_result in frame_results:
                        filename = os.path.basename(frame_result['frame_path'])
                        rel_img_path = f"{frames_rel_path}/{filename}"

                        inspection_image = InspectionImage.objects.create(
                            inspection=inspection,
                            image=rel_img_path,
                            processed_image=rel_img_path,
                        )

                        for detection in frame_result['detections']:
                            detection['image_obj'] = inspection_image
                            detections.append(detection)
                except Exception as exc:
                    detector_error = str(exc)
                    print(f"Video Processing Error: {exc}")

        elif image_file:
            inspection_image = InspectionImage.objects.create(
                inspection=inspection,
                image=image_file,
            )

            if detector:
                try:
                    today = timezone.now().date()
                    date_path = today.strftime('%Y/%m/%d')
                    filename = os.path.basename(inspection_image.image.path)
                    rel_processed_path = f"inspections/processed/{date_path}/{inspection.id}_{filename}"
                    full_processed_path = os.path.join(settings.MEDIA_ROOT, rel_processed_path)

                    image_detections = detector.detect(
                        inspection_image.image.path,
                        output_path=full_processed_path,
                    )

                    if os.path.exists(full_processed_path):
                        inspection_image.processed_image = rel_processed_path
                        inspection_image.save(update_fields=['processed_image'])

                    for detection in image_detections:
                        detection['image_obj'] = inspection_image
                        detections.append(detection)
                except Exception as exc:
                    detector_error = str(exc)
                    print(f"Image detection failed: {exc}")

        advisor = _get_gemini_advisor_class()() if detections else None
        saved_detection_logs = []
        highest_severity = RiskLevel.SAFE

        for detection in detections:
            raw_label = detection.get('label', 'Unknown')
            confidence = float(detection.get('confidence', 0.0))
            bbox = detection.get('bbox') or {}
            detected_at_utc = detection.get('detected_at_utc') or utc_now_iso()
            inspection_image = detection.get('image_obj')

            object_type, severity = classify_detection_label(raw_label)
            det_sev = detection.get('severity')
            if det_sev == 'Safe':
                severity = RiskLevel.SAFE
            elif det_sev == 'Low':
                severity = RiskLevel.LOW
            elif det_sev == 'Medium':
                severity = RiskLevel.MEDIUM
            elif det_sev == 'High':
                severity = RiskLevel.HIGH
            suggestion = _generate_suggestion(advisor, object_type, severity)

            detected_object = DetectedObject.objects.create(
                image=inspection_image,
                raw_label=raw_label,
                object_type=object_type,
                confidence=confidence,
                severity=severity,
                detected_at=_parse_detected_at(detected_at_utc),
                frame_index=detection.get('frame_index', 0) or 0,
                frame_timestamp_seconds=detection.get('frame_timestamp_seconds'),
                bbox_x=_coerce_int(bbox.get('x')),
                bbox_y=_coerce_int(bbox.get('y')),
                bbox_w=_coerce_int(bbox.get('w')),
                bbox_h=_coerce_int(bbox.get('h')),
                bbox_x1=_coerce_int(bbox.get('x1')),
                bbox_y1=_coerce_int(bbox.get('y1')),
                bbox_x2=_coerce_int(bbox.get('x2')),
                bbox_y2=_coerce_int(bbox.get('y2')),
                bbox_data={
                    'x': _coerce_int(bbox.get('x')),
                    'y': _coerce_int(bbox.get('y')),
                    'w': _coerce_int(bbox.get('w')),
                    'h': _coerce_int(bbox.get('h')),
                    'x1': _coerce_int(bbox.get('x1')),
                    'y1': _coerce_int(bbox.get('y1')),
                    'x2': _coerce_int(bbox.get('x2')),
                    'y2': _coerce_int(bbox.get('y2')),
                },
                gemini_suggestion=suggestion,
            )

            saved_detection_logs.append(
                build_detection_log_entry(
                    inspection_image=inspection_image,
                    raw_label=raw_label,
                    object_type=object_type,
                    severity=severity,
                    confidence=confidence,
                    detected_at_utc=detected_at_utc,
                    frame_index=detected_object.frame_index,
                    frame_timestamp_seconds=detected_object.frame_timestamp_seconds,
                    bbox=detected_object.bbox_data,
                    gemini_suggestion=suggestion,
                )
            )

            highest_severity = highest_risk_level([highest_severity, severity])

        if detections:
            inspection.risk_level = highest_severity
            inspection.status = Inspection.Status.ALERT if is_alert_level(highest_severity) else Inspection.Status.COMPLETED
        else:
            inspection.status = Inspection.Status.COMPLETED
            inspection.risk_level = RiskLevel.SAFE

        source_type = 'image' if image_file else 'video' if video_file else 'unknown'
        source_name = getattr(image_file or video_file, 'name', None)

        inspection.analysis_log = build_analysis_log(
            source_type=source_type,
            source_name=source_name,
            detections=saved_detection_logs,
            detector_error=detector_error,
        )
        inspection.analysis_log['inspection_status'] = inspection.status
        inspection.analysis_log['inspection_risk_level'] = inspection.risk_level
        inspection.save()
        broadcast_inspection_alert(inspection, saved_detection_logs)

        serializer = InspectionSerializer(inspection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

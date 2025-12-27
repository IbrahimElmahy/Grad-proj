from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Inspection, InspectionImage, DetectedObject, RiskLevel
from .serializers import InspectionSerializer
from ai_engine.gemini_service import GeminiAdvisor
import random

class InspectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows inspections to be viewed.
    """
    queryset = Inspection.objects.all().order_by('-timestamp')
    serializer_class = InspectionSerializer

class UploadInspectionView(APIView):
    """
    API endpoint for cameras/mobile to upload inspection images.
    Triggers AI analysis automatically.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        camera_id = request.data.get('camera_id', 'Unknown Camera')
        image_file = request.data.get('image')
        video_file = request.data.get('video')

        if not image_file and not video_file:
            return Response({'error': 'No image or video provided'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create Inspection Record
        inspection = Inspection.objects.create(
            camera_id=camera_id,
            status='PROCESSING',
            risk_level=RiskLevel.SAFE 
        )

        detections = []
        detector = None
        
        # Initialize Detector if needed
        from ai_engine.yolo_service import YoloDetector
        try:
            detector = YoloDetector()
        except:
            print("Failed to load YOLO model")

        # 2. Handle VIDEO
        if video_file:
            inspection.video = video_file
            inspection.save()
            
            if detector:
                # We need a path to save extracted frames
                try:
                    import os
                    import datetime
                    from django.conf import settings
                    
                    today = datetime.date.today()
                    date_path = today.strftime('%Y/%m/%d')
                    frames_rel_path = f"inspections/processed/{date_path}/{inspection.id}"
                    output_dir_base = os.path.join(settings.MEDIA_ROOT, frames_rel_path)
                    
                    video_path = inspection.video.path
                    frame_results = detector.detect_video(video_path, output_dir_base)
                    
                    for fr in frame_results:
                        fname = os.path.basename(fr['frame_path'])
                        rel_img_path = f"{frames_rel_path}/{fname}"
                        
                        img_obj = InspectionImage.objects.create(
                            inspection=inspection,
                            image=rel_img_path
                        )
                        
                        for det in fr['detections']:
                            detections.append({
                                'label': det['label'],
                                'confidence': det['confidence'],
                                'bbox': det['bbox'],
                                'image_obj': img_obj
                            })
                except Exception as e:
                    print(f"Video Processing Error: {e}")

        # 3. Handle IMAGE
        elif image_file:
            inspection_image = InspectionImage.objects.create(
                inspection=inspection,
                image=image_file
            )
            
            if detector:
                try:
                    img_detections = detector.detect(inspection_image.image.path)
                    for d in img_detections:
                        d['image_obj'] = inspection_image
                        detections.append(d)
                except Exception as e:
                    print(f"Image detection failed: {e}")

        # 4. Save Detections
        highest_severity = RiskLevel.SAFE
        has_alert = False

        if detections:
            advisor = GeminiAdvisor()
            
            for det in detections:
                obj_type = det['label']
                confidence = det['confidence']
                img_obj = det.get('image_obj')
                
                # Mapping logic
                severity = RiskLevel.LOW
                mapped_type = 'OTHER'
                lbl = obj_type.lower()
                
                if 'fod' in lbl or 'undefined' in lbl or 'debris' in lbl:
                    mapped_type = 'FOD'
                    severity = RiskLevel.HIGH
                elif 'bird' in lbl:
                    mapped_type = 'BIRD'
                    severity = RiskLevel.MEDIUM
                elif 'aircraft' in lbl or 'airplane' in lbl:
                    mapped_type = 'AIRCRAFT'
                    severity = RiskLevel.SAFE # Aircraft on runway are usually safe/normal unless stated otherwise
                elif 'vehicle' in lbl:
                    mapped_type = 'VEHICLE'
                    severity = RiskLevel.LOW
                elif 'crack' in lbl:
                    mapped_type = 'CRACK'
                    severity = RiskLevel.MEDIUM
                else:
                    mapped_type = 'OTHER'
                    severity = RiskLevel.LOW
                    
                suggestion = ""
                # Optional: trigger Gemini suggestions here

                DetectedObject.objects.create(
                    image=img_obj,
                    object_type=mapped_type,
                    confidence=confidence,
                    severity=severity,
                    bbox_data=det['bbox'],
                    gemini_suggestion=suggestion
                )
                
                if severity == RiskLevel.HIGH:
                    highest_severity = RiskLevel.HIGH
                    has_alert = True
                elif severity == RiskLevel.MEDIUM and highest_severity != RiskLevel.HIGH:
                    highest_severity = RiskLevel.MEDIUM
                    has_alert = True

            if has_alert:
                inspection.status = 'ALERT'
                inspection.risk_level = highest_severity
            else:
                inspection.status = 'COMPLETED'
                inspection.risk_level = RiskLevel.SAFE
        else:
            inspection.status = 'COMPLETED'
            inspection.risk_level = RiskLevel.SAFE
            
        inspection.save()
        serializer = InspectionSerializer(inspection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

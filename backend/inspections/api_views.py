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
                    import os
                    from django.conf import settings
                    import datetime
                    
                    # Prepare path for processed image
                    today = datetime.date.today()
                    date_path = today.strftime('%Y/%m/%d')
                    fname = os.path.basename(inspection_image.image.path)
                    
                    # Store in inspections/processed/...
                    rel_processed_path = f"inspections/processed/{date_path}/{inspection.id}_{fname}"
                    full_processed_path = os.path.join(settings.MEDIA_ROOT, rel_processed_path)
                    
                    # Run detection + Save processed image
                    img_detections = detector.detect(inspection_image.image.path, output_path=full_processed_path)
                    
                    # Update model with processed image path
                    if os.path.exists(full_processed_path):
                        inspection_image.processed_image = rel_processed_path
                        inspection_image.save()
                    
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
                
                # Model classes: Runway, aircraft, bird, vehicle
                if 'bird' in lbl:
                    mapped_type = 'BIRD'
                    severity = RiskLevel.HIGH # Birds are high risk on runway
                elif 'aircraft' in lbl:
                    mapped_type = 'AIRCRAFT'
                    severity = RiskLevel.SAFE # Normal unless conflict, but marked SAFE for now
                elif 'vehicle' in lbl:
                    mapped_type = 'VEHICLE'
                    severity = RiskLevel.MEDIUM # Vehicle on runway is a hazard
                elif 'runway' in lbl:
                    mapped_type = 'RUNWAY'
                    severity = RiskLevel.SAFE
                else:
                    mapped_type = 'OTHER'
                    severity = RiskLevel.LOW
                    
                suggestion = ""
                if severity == RiskLevel.HIGH:
                    suggestion = "Immediate action required: Dispatch bird scaring unit."
                elif severity == RiskLevel.MEDIUM:
                    suggestion = "Warning: Check for unauthorized vehicle access."

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

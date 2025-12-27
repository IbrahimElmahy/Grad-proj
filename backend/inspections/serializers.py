from rest_framework import serializers
from .models import Inspection, InspectionImage, DetectedObject

class DetectedObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectedObject
        fields = ['id', 'object_type', 'confidence', 'severity', 'bbox_data', 'gemini_suggestion']

class InspectionImageSerializer(serializers.ModelSerializer):
    detected_objects = DetectedObjectSerializer(many=True, read_only=True)

    class Meta:
        model = InspectionImage
        fields = ['id', 'image', 'processed_image', 'created_at', 'detected_objects']

class InspectionSerializer(serializers.ModelSerializer):
    images = InspectionImageSerializer(many=True, read_only=True)
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Inspection
        fields = ['id', 'camera_id', 'timestamp', 'status', 'risk_level', 'images']

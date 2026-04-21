from rest_framework import serializers
from .models import Inspection, InspectionImage, DetectedObject

class DetectedObjectSerializer(serializers.ModelSerializer):
    detected_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)
    bbox_xywh = serializers.SerializerMethodField()
    bbox_xyxy = serializers.SerializerMethodField()

    class Meta:
        model = DetectedObject
        fields = [
            'id',
            'raw_label',
            'object_type',
            'confidence',
            'severity',
            'detected_at',
            'frame_index',
            'frame_timestamp_seconds',
            'bbox_x',
            'bbox_y',
            'bbox_w',
            'bbox_h',
            'bbox_x1',
            'bbox_y1',
            'bbox_x2',
            'bbox_y2',
            'bbox_xywh',
            'bbox_xyxy',
            'bbox_data',
            'gemini_suggestion',
        ]

    def get_bbox_xywh(self, obj):
        return {
            'x': obj.bbox_x,
            'y': obj.bbox_y,
            'w': obj.bbox_w,
            'h': obj.bbox_h,
        }

    def get_bbox_xyxy(self, obj):
        return {
            'x1': obj.bbox_x1,
            'y1': obj.bbox_y1,
            'x2': obj.bbox_x2,
            'y2': obj.bbox_y2,
        }

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
        fields = ['id', 'camera_id', 'timestamp', 'status', 'risk_level', 'analysis_log', 'video', 'images']

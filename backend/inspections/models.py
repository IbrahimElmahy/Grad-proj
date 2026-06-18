from django.db import models
import uuid

class RiskLevel(models.TextChoices):
    HIGH = 'HIGH', 'High Risk'
    MEDIUM = 'MEDIUM', 'Medium Risk'
    LOW = 'LOW', 'Low Risk'
    SAFE = 'SAFE', 'Safe'

class ObjectType(models.TextChoices):
    DEBRIS = 'DEBRIS', 'Debris'
    FOD = 'FOD', 'Foreign Object Debris'
    WILDLIFE_BIRDS = 'WILDLIFE_BIRDS', 'Wildlife / Birds'
    BIRD = 'BIRD', 'Bird/Wildlife'
    CRACK = 'CRACK', 'Crack'
    POTHOLE = 'POTHOLE', 'Pothole'
    VEHICLE = 'VEHICLE', 'Vehicle'
    LUGGAGE = 'LUGGAGE', 'Luggage'
    PERSONNEL = 'PERSONNEL', 'Personnel'
    AIRCRAFT = 'AIRCRAFT', 'Aircraft'
    FUEL_SPILL = 'FUEL_SPILL', 'Fuel Spill'
    STANDING_WATER = 'STANDING_WATER', 'Standing Water'
    TOOL_EQUIPMENT = 'TOOL_EQUIPMENT', 'Tool Equipment'
    CONE_OR_BARRIER = 'CONE_OR_BARRIER', 'Cone or Barrier'
    PERSON = 'PERSON', 'Person'
    RUNWAY = 'RUNWAY', 'Runway'
    OTHER = 'OTHER', 'Other'

class Inspection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera_id = models.CharField(max_length=100, help_text="ID of the camera/device capturing the image")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Status(models.TextChoices):
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        ALERT = 'ALERT', 'Alert (Risk Detected)'
        
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROCESSING)
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices, default=RiskLevel.SAFE)
    analysis_log = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured JSON log of detections, severity, coordinates, and timestamps.",
    )
    
    # New Video Field
    video = models.FileField(upload_to='inspections/videos/%Y/%m/%d/', null=True, blank=True, max_length=500)
    processed_video = models.FileField(upload_to='inspections/processed_videos/%Y/%m/%d/', null=True, blank=True, max_length=500)
    
    def __str__(self):
        return f"Inspection {self.id} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-timestamp']

class InspectionImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='images')
    
    # Original image from the camera
    image = models.ImageField(upload_to='inspections/raw/%Y/%m/%d/', max_length=500)
    
    # Processed image (optional, populated after AI analysis)
    processed_image = models.ImageField(upload_to='inspections/processed/%Y/%m/%d/', null=True, blank=True, max_length=500)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.inspection.id}"

class DetectedObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ForeignKey(InspectionImage, on_delete=models.CASCADE, related_name='detected_objects')
    
    raw_label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Original class label emitted by the YOLO model.",
    )
    object_type = models.CharField(max_length=30, choices=ObjectType.choices)
    confidence = models.FloatField(help_text="Confidence score from 0.0 to 1.0")
    
    severity = models.CharField(max_length=10, choices=RiskLevel.choices, default=RiskLevel.LOW)
    detected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="UTC timestamp when the model reported this detection.",
    )
    frame_index = models.PositiveIntegerField(
        default=0,
        help_text="Zero-based frame index for video detections. Images default to 0.",
    )
    frame_timestamp_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Timestamp of the video frame in seconds.",
    )
    bbox_x = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Top-left X coordinate in pixels.",
    )
    bbox_y = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Top-left Y coordinate in pixels.",
    )
    bbox_w = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Bounding box width in pixels.",
    )
    bbox_h = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Bounding box height in pixels.",
    )
    bbox_x1 = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum X coordinate in pixels.",
    )
    bbox_y1 = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum Y coordinate in pixels.",
    )
    bbox_x2 = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum X coordinate in pixels.",
    )
    bbox_y2 = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum Y coordinate in pixels.",
    )
    
    # Bounding Box Data retained for backward compatibility and API convenience.
    bbox_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="{'x': 10, 'y': 20, 'w': 30, 'h': 40, 'x1': 10, 'y1': 20, 'x2': 40, 'y2': 60}",
    )
    
    # Gemini Integration
    gemini_suggestion = models.TextField(blank=True, null=True, help_text="AI suggested solution for this hazard")

    def __str__(self):
        label = self.raw_label or self.object_type
        return f"{label} ({self.severity}) - {self.confidence:.2f}"

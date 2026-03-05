from django.db import models
import uuid

class RiskLevel(models.TextChoices):
    HIGH = 'HIGH', 'High Risk'
    MEDIUM = 'MEDIUM', 'Medium Risk'
    LOW = 'LOW', 'Low Risk'
    SAFE = 'SAFE', 'Safe'

class ObjectType(models.TextChoices):
    FOD = 'FOD', 'Foreign Object Debris'
    BIRD = 'BIRD', 'Bird/Wildlife'
    CRACK = 'CRACK', 'Crack'
    POTHOLE = 'POTHOLE', 'Pothole'
    VEHICLE = 'VEHICLE', 'Vehicle'
    AIRCRAFT = 'AIRCRAFT', 'Aircraft'
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
    
    # New Video Field
    video = models.FileField(upload_to='inspections/videos/%Y/%m/%d/', null=True, blank=True, max_length=500)
    
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
    
    object_type = models.CharField(max_length=20, choices=ObjectType.choices)
    confidence = models.FloatField(help_text="Confidence score from 0.0 to 1.0")
    
    severity = models.CharField(max_length=10, choices=RiskLevel.choices, default=RiskLevel.LOW)
    
    # Bounding Box Data (normalized coordinates 0-1)
    # We use JSONField to store x, y, width, height flexibly
    bbox_data = models.JSONField(default=dict, help_text="{'x': 0.5, 'y': 0.5, 'width': 0.1, 'height': 0.2}")
    
    # Gemini Integration
    gemini_suggestion = models.TextField(blank=True, null=True, help_text="AI suggested solution for this hazard")

    def __str__(self):
        return f"{self.object_type} ({self.severity}) - {self.confidence:.2f}"

from django.core.management.base import BaseCommand
from inspections.models import Inspection, InspectionImage, DetectedObject, RiskLevel, ObjectType
from django.utils import timezone
import random
import uuid
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with dummy inspection data'

    def handle(self, *args, **options):
        self.stdout.write('Deleting old data...')
        Inspection.objects.all().delete()
        
        self.stdout.write('Creating new dummy data...')
        
        cameras = ['CAM-01 (North)', 'CAM-02 (South)', 'Drone-Alpha', 'Mobile-Unit-05']
        
        # Create 20 Inspections
        for i in range(20):
            status = random.choice(['COMPLETED', 'COMPLETED', 'ALERT', 'PROCESSING'])
            risk = RiskLevel.SAFE
            if status == 'ALERT':
                risk = random.choice([RiskLevel.HIGH, RiskLevel.MEDIUM])
            
            # Random time in last 24 hours
            time_offset = random.randint(0, 1440)
            timestamp = timezone.now() - timedelta(minutes=time_offset)
            
            inspection = Inspection.objects.create(
                camera_id=random.choice(cameras),
                status=status,
                risk_level=risk
            )
            # Manually set timestamp (auto_now_add prevents this on create usually, so we update)
            inspection.timestamp = timestamp
            inspection.save()

            # Create 1-2 Images
            for j in range(random.randint(1, 2)):
                img = InspectionImage.objects.create(
                    inspection=inspection,
                    image='inspections/raw/dummy.jpg' # Placeholder
                )
                
                # If high risk, add defects
                if risk != RiskLevel.SAFE:
                    # Add 1-3 defects
                    for k in range(random.randint(1, 3)):
                        obj_type = random.choice(ObjectType.choices)[0]
                        confidence = random.uniform(0.75, 0.99)
                        
                        suggestion = ""
                        if obj_type == 'FOD':
                            suggestion = "Dispatch ground crew to remove debris immediately."
                        elif obj_type == 'CRACK':
                            suggestion = "Seal crack with rubberized asphalt sealant to prevent water intrusion."
                        elif obj_type == 'BIRD':
                            suggestion = "Deploy bird deterrence measures (sonic cannon) and monitor."
                            
                        DetectedObject.objects.create(
                            image=img,
                            object_type=obj_type,
                            confidence=confidence,
                            severity=risk,
                            bbox_data={'x': random.uniform(0.1, 0.9), 'y': random.uniform(0.1, 0.9), 'w': 0.1, 'h': 0.1},
                            gemini_suggestion=suggestion
                        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created 20 dummy inspections!'))

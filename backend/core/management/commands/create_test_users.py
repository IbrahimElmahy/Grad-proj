from django.core.management.base import BaseCommand
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates test users for development'

    def handle(self, *args, **options):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from inspections.models import Inspection, DetectedObject

        # 1. Setup 'Managers' Group
        manager_group, _ = Group.objects.get_or_create(name='Managers')
        # Give all permissions for inspection app
        inspection_ct = ContentType.objects.get_for_model(Inspection)
        detected_obj_ct = ContentType.objects.get_for_model(DetectedObject)
        
        permissions = Permission.objects.filter(content_type__in=[inspection_ct, detected_obj_ct])
        manager_group.permissions.set(permissions)
        self.stdout.write("Configured 'Managers' group permissions.")

        # 2. Setup 'Safety Officers' Group
        officer_group, _ = Group.objects.get_or_create(name='Safety Officers')
        # Give only View/Add permissions
        officer_perms = Permission.objects.filter(
            content_type__in=[inspection_ct, detected_obj_ct],
            codename__in=['view_inspection', 'add_inspection', 'view_detectedobject', 'add_detectedobject']
        )
        officer_group.permissions.set(officer_perms)
        self.stdout.write("Configured 'Safety Officers' group permissions.")

        # 3. Create Manager User
        user, created = User.objects.get_or_create(username='manager', defaults={'email': 'manager@rvms.com'})
        if created:
            user.set_password('manager123')
        user.is_staff = True
        user.save()
        user.groups.add(manager_group)
        self.stdout.write(self.style.SUCCESS(f"User 'manager' updated (Group: Managers)"))

        # 4. Create Safety Officer User
        user, created = User.objects.get_or_create(username='officer', defaults={'email': 'officer@rvms.com'})
        if created:
            user.set_password('officer123')
        user.is_staff = True 
        user.save()
        user.groups.add(officer_group)
        self.stdout.write(self.style.SUCCESS(f"User 'officer' updated (Group: Safety Officers)"))

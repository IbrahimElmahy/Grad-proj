from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SystemSettings

admin.site.register(User, UserAdmin)

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow adding if it doesn't exist yet
        if SystemSettings.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the settings
        return False

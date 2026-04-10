from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class SystemSettings(models.Model):
    singleton_id = models.IntegerField(default=1, unique=True)
    gemini_api_key = models.CharField(max_length=255, blank=True, null=True, help_text="Enter your Google Gemini API Key here")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.singleton_id = 1
        super(SystemSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(singleton_id=1)
        return obj

    def __str__(self):
        return "System Configuration"

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

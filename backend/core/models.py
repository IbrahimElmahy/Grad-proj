from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


def generate_reset_token():
    return uuid.uuid4().hex

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


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.CharField(max_length=64, unique=True, default=generate_reset_token)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])

    def __str__(self):
        return f"Password reset token for {self.user.username}"

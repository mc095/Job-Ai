from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture_url = models.URLField(blank=True, null=True)
    resume_text = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)  # create profile
    else:
        # Only update if profile exists
        if hasattr(instance, "userprofile"):
            instance.userprofile.save()

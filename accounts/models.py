from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    first = models.CharField(max_length=255, default='None')
    last = models.CharField(max_length=255, default='None')
    email = models.EmailField(default='None')
    birthday = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    pfp = models.ImageField(null=True, blank=True)
    user = models.OneToOneField(User, models.CASCADE)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print(instance)
        UserProfile.objects.create(user=instance).save() #pylint: disable=E1101

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

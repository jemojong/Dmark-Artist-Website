from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save,sender=User)
def create_profile(sender,instance,created,**kwargs):
    print ("Created: ",created)
    if created:
        UserProfile.objects.create(user=instance)


from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    email = models.EmailField(max_length=30,blank=True)
    artist_name = models.CharField(max_length=60,default="nill")
    
    def __str__(self):
        return self.artist_name

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()



class ArtistAlias(models.Model):
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name="user_artist")
    alias = models.CharField(max_length=120,null=True,blank=True,unique=True)

    def __str__(self):
        return self.alias

class ArtistProfile(models.Model):
    artist = models.CharField(max_length=120)
    song = models.CharField(max_length=120)
    price = models.IntegerField()
    downloads = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)
    month = models.CharField(max_length=120)
    year = models.IntegerField()
    company = models.CharField(max_length=120)
    

    def __str__(self):
        return self.artist

class ArtistProfileBulkUpload(models.Model):
    uploaded = models.ForeignKey(ArtistProfile, null=True, on_delete=models.CASCADE,related_name='uploaded_data')
    date_uploaded = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='artists/bulkupload/%Y%m')
    year = models.CharField(max_length=20,null=True)
    month = models.CharField(max_length=20,null=True)
    #file_name = models.CharField(max_length=150, unique=True)
    def __str__(self):
        return self.year + self.month
    
  


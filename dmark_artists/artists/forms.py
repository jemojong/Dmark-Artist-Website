from django import forms
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User
from .models import UserProfile,ArtistProfileBulkUpload,ArtistAlias,ArtistProfile

class UserProfileForm(UserCreationForm):
    #email = forms.EmailField()
    artist_name = forms.CharField(max_length=30)
    class Meta:
        model = User
        fields =('username','email','artist_name','password1', 'password2',)


class ArtistProfileBulkUploadForm(forms.ModelForm):
  class Meta:
    model = ArtistProfileBulkUpload
    fields = ("file",'month','year')
  

class ArtistAliasForm(forms.ModelForm):
  class Meta:
    model = ArtistAlias
    fields ="__all__"
  
class UserProfileUpdateForm(forms.ModelForm):
    #email = forms.EmailField()
    artist_name = forms.CharField(max_length=30)
    class Meta:
        model = UserProfile
        fields ="__all__"

class ArtistProfileForm(forms.ModelForm):
  class Meta:
    model = ArtistProfile
    fields ="__all__"
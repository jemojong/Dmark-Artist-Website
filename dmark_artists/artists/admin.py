from django.contrib import admin
from .models import ArtistProfile,ArtistAlias,UserProfile,ArtistProfileBulkUpload

# Register your models here.
from .models import ArtistProfile
from import_export.admin import ImportExportModelAdmin

from import_export import resources

class ArtistProfileResource(resources.ModelResource):

    class Meta:
        model = ArtistProfile

class ArtistProfileAdmin(ImportExportModelAdmin):
    resource_class = ArtistProfileResource

admin.site.register(ArtistProfile, ArtistProfileAdmin)

#admin.site.register(ArtistProfile)
admin.site.register(ArtistAlias)
admin.site.register(UserProfile)
admin.site.register(ArtistProfileBulkUpload)

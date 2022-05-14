from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import ArtistProfile

class ImportSpec(resources.ModelResource):
    class Meta:
        model = ArtistProfile
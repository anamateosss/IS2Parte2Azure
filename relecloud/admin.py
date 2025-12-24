from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Cruise)
admin.site.register(models.Destination)
admin.site.register(models.InfoRequest)
admin.site.register(models.Purchase)
admin.site.register(models.DestinationReview)
admin.site.register(models.CruiseReview)

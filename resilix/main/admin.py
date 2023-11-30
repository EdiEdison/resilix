from django.contrib import admin

from .models import *

admin.site.register(Alert)
admin.site.register(DisasterFeedback)
admin.site.register(Location)
admin.site.register(CustomUser)
admin.site.register(AlertChoices)

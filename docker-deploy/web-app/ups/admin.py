from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import *

admin.site.register(User)
admin.site.register(Package)
admin.site.register(Truck)
admin.site.register(Warehouse)
admin.site.register(World)
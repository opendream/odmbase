
from django.contrib import admin

from .models import PrivateMessage


@admin.register(PrivateMessage)
class MessageAdmin(admin.ModelAdmin):
    pass

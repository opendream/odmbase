from django.contrib import admin

from odmbase.account.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
from django.contrib import admin

from account.models import User
from odmbase.account.admin import UserAdmin as ODMUserAdmin


@admin.register(User)
class UserAdmin(ODMUserAdmin):
    additional_fields = ()

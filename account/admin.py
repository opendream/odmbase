from django.contrib import admin

try:
    from account.models import User
except ImportError:
    from odmbase.account.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
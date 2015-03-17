
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from account.models import User
from odmbase.account.forms import UserChangeForm, UserCreationForm


class UserAdmin(UserAdmin):
    additional_fields = ()
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, 
            {'fields': ('username', 'password', 'email')}
        ),
        ('Personal Info', 
            {'fields': ('first_name', 'last_name', 'image')}
        ),
        ('Permissions', 
            {'fields': ('is_superuser', 'is_staff', 'is_deleted', 'status', 'groups', 'user_permissions')}
        ),
        ('Priority', 
            {'fields': ('priority', 'ordering')}
        ),
        ('Important dates', 
            {'fields': ('date_joined', 'last_login')}
        ),
    )

    form = UserChangeForm
    add_form = UserCreationForm
    list_filter = ('is_staff', 'is_superuser', 'status', 'groups')

    def __init__(self, *args, **kwargs):
        if self.additional_fields:
            self.fieldsets += ('Others',
                {'fields': self.additional_fields}
            ),
        super(UserAdmin, self).__init__(*args, **kwargs)
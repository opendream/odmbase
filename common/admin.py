from django.contrib import admin

from odmbase.common.models import CommonModel, Image


@admin.register(CommonModel)
class CommonAdmin(admin.ModelAdmin):
    pass


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass
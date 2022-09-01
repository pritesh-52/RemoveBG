from django.contrib import admin
from api.models import File

# class FileAdmin(admin.ModelAdmin):
#     class Meta:
#         model = File
#         fields = ('image_tag',)
#         readonly_fields = ('image_tag',)
#
#     def image_tag(self, obj):
#         from django.utils.html import escape
#         return u'<img src="%s" />' % escape(obj.file.url)
#
#     image_tag.short_description = 'Image'

from django.utils.html import format_html


@admin.register(File)
class FileAdmin(admin.ModelAdmin):

    def original_image(self, obj):
        return format_html('<img src="{}" width="10%" height="10%"  />'.format(obj.original_image.url))

    def procees_image(self, obj):
        return format_html('<img src="{}" width="10%" height="10%"  />'.format(obj.original_image.url))

    original_image.short_description = 'Image'

    list_display = ['original_image', 'processed_image', 'remark']

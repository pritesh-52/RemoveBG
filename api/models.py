import os.path

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class File(models.Model):
    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("All Images")

    original_image = models.FileField(blank=False, null=False, verbose_name=_("Original image"))
    processed_image = models.FileField(blank=False, null=False, verbose_name=_("Processed image"))
    remark = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_os_path(self):
        return os.path.join(settings.MEDIA_ROOT, str(self.original_image))  # for development ONLY

    def get_file_name(self):
        return str(self.original_image)

    def __str__(self):
        return self.remark


@receiver(post_delete, sender=File)
def delete_file(sender, instance, **kwargs):
    try:
        if instance.original_image and instance.processed_image:
            instance.original_image.delete(False)
            instance.processed_image.delete(False)
    except Exception as error:
        print(error)

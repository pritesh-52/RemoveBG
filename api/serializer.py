from rest_framework import serializers

from api.models import File


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ('original_image', 'remark', 'timestamp')


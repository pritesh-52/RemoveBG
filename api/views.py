import io
from time import sleep

from django.core.files import File  # you need this somewhere
from django.core.files.base import ContentFile

from rembg.bg import remove
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
import asyncio
from asgiref.sync import sync_to_async
import os
from django.http import HttpResponse
from django.conf import settings

from api.models import File
from api.serializer import FileSerializer

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


async def async_rembg(remark):
    file = await sync_to_async(File.objects.get, thread_sensitive=True)(remark=remark)
    input_path = file.get_os_path()
    input_name = file.get_file_name()
    input = Image.open(input_path)
    output = remove(input)
    output.save(input_path, 'PNG')
    file.delete()
    return {'path': input_path,
            'name': input_name,
            }


def image_to_byte_array(image: Image) -> bytes:
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def sync_rembg(remark, original_image):
    sleep(2)
    file = File.objects.filter(original_image=original_image).first()
    if file is None:
        file = File.objects.filter(remark=remark).first()
    input_path = file.get_os_path()
    input_name = file.get_file_name()
    image_input = Image.open(input_path)
    input = image_to_byte_array(image_input)
    output = remove(input)
    # image_stream = io.BytesIO(output.tobytes())
    # image_file = Image.open(image_stream)
    # if image_file.mode != "RGB":
    #     image_file = image_file.convert("RGB")
    processed_image_path = input_path.split('.')[0] + 'processed.png'
    with open(processed_image_path, 'wb') as o:
        o.write(output)
    file.original_image = original_image
    file.processed_image = processed_image_path.split('/')[-1]
    file.save()
    return {'path': '/media/' + processed_image_path.split('/')[-1],
            'name': input_name,
            }


def clear_media():
    media_path = settings.MEDIA_ROOT
    for files in os.scandir(media_path):
        os.remove(files)
        return media_path + 'is clear !'


class FileView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = FileSerializer(data=request.data, context={"request": request})
        if file_serializer.is_valid():
            cd = file_serializer.validated_data
            file_serializer.save()
            processed_image_data = sync_rembg(cd['remark'], cd['original_image'])
            # rembg_status = asyncio.run(async_rembg(cd['remark']))

            processed_image = request.build_absolute_uri(processed_image_data['path'])
            data = file_serializer.data
            data['processed_image'] = processed_image
            return Response(data)
            # with open(path, 'rb') as image:
            #     file = image.read()
            #     response = HttpResponse(file, content_type='image/png')
            #     filename = rembg_status['name']
            #     response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
            #     return response
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.urls import path
from api.views import FileView


app_name = 'file_uploader'


urlpatterns = [
    path('upload/', FileView.as_view(), name='file-upload'),
]
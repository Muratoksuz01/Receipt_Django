from django.urls import path
from .views import upload_and_process_image,save_data

urlpatterns = [
    path('upload/', upload_and_process_image, name='upload_image'),
    path("send-data/",save_data,name="save_data"),
]

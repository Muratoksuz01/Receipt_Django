from django.db import models

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')  # uploads/ klasörüne kaydedilecek
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Yükleme tarihi






class Snippet(models.Model):
    time = models.TextField()
    date = models.TextField()
    address = models.TextField()
    items = models.TextField()
    total = models.TextField()
   
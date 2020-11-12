from django.db import models
from app_object_detection.object_detection import object_detection

# Create your models here.


class Detector(models.Model):
    det = object_detection()
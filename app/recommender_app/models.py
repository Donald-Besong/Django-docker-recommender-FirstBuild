from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User  # this creates the table auth_user after migrate
import sys
import os
sys.path.append("..")
from donald_project import settings
from .validators import validate_file_extension
from django.core.validators import MaxValueValidator, MinValueValidator
from io import BytesIO
import inspect

def get_s3_mediafile(myfile='static/csv_files/user_ratings.csv'):
    # print("******** hello from ****{}**************".format(inspect.stack()[0][3]))
    import boto3
    s3_client = boto3.client(
        's3',
        region_name='eu-west-1',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    # buckets = s3_client.list_objects(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
    data = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=myfile)
    return data, myfile

def get_mediafile():
    return str(settings.MEDIA_ROOT) + '/user_ratings.csv'

# table blog_post will be created after migration
class Post(models.Model):  # many to ****
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    # date_posted = models.DateTimeField(auto_now_add==True) #this date is fixed
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # ***one

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

class MoviesRead(models.Model):
    if settings.USE_S3:
        default_file = get_s3_mediafile()
    else:
        default_file = get_mediafile()
    # print("**** type of deafault file from models.PdfRead".format(type(default_file)))
    title = models.CharField(max_length=100)
    file_name = models.FileField(default=default_file, upload_to="csv_files")
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # ***one

    def __str__(self):
        return self.title

    # def get_absolute_url(self):
    # return reverse('post-detail', kwargs={'pk': self.pk})

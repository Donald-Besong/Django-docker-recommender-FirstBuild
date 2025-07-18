from django.contrib import admin
from .models import Post

# Register your models here. #note that we don't have to register User. It is automaticall registered as Users
admin.site.register(Post)

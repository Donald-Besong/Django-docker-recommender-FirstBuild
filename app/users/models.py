from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):  # users_profile table will be created
    # and will relate to the auth_user table
    # this is connected to url 'profile' because it has the same name
    # note that django's ImageField imports Pillow on the backend use
    # so you have to install PIL but do not import
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    # def save(self, *arg, **kwargs):
        # super().save(*arg, **kwargs)

        # img = Image.open(self.image.path)

        # if img.height > 300 or img.width > 300:
            # output_size = (300, 300)
            # img.thumbnail(output_size)
            # img.save(self.image.path)

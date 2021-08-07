import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from trainees_one.settings import BASE_DIR


class UserProfile(models.Model):
    genders = [
        ('Male', 'ml'),
        ('Female', 'fm'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    image = models.ImageField(upload_to='images', verbose_name='Изображение')
    gender = models.CharField(choices=genders, default='ml', max_length=7, verbose_name='Пол')
    long = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True, verbose_name='Долгота')
    lat = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True, verbose_name='Широта')

    def save(self, *args, **kwargs):
        """Чтобы добавлялась ватермарка, нужно добавить любое изображение с названием index.jpeg
        в каталог /media/watermark"""
        try:
            original_image = Image.open(self.image)
            watermark = Image.open(os.path.join(BASE_DIR, 'media/watermark/index.jpeg'))
            original_image_x, original_image_y = original_image.size
            watermark_x, watermark_y = watermark.size
            scale = 10
            watermark_scale = max(original_image_x / (scale * watermark_x), original_image_y / (scale * watermark_y))
            new_size = (int(watermark_x * watermark_scale), int(watermark_y * watermark_scale))
            rgba_watermark = watermark.resize(new_size, resample=Image.ANTIALIAS)
            rgba_watermark_mask = rgba_watermark.convert("L").point(lambda x: min(x, 180))
            rgba_watermark.putalpha(rgba_watermark_mask)
            image_name = self.image
            original_image.paste(rgba_watermark, (0, 0), rgba_watermark_mask)
            original_image.save(os.path.join(BASE_DIR, f'media/images/{image_name}'))
            self.image = f'images/{image_name}'
        except Exception as ex:
            pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.first_name = instance.first_name
    instance.userprofile.last_name = instance.last_name
    instance.userprofile.save()


class MatchUsers(models.Model):
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='put_like', verbose_name='Поставивший лайк')
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='get_like', verbose_name='Получивший лайк')

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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

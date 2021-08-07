from rest_framework.serializers import ModelSerializer, DecimalField, CharField, EmailField, \
    ValidationError, ImageField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import *
from trainees_one.celery import celery_app
from PIL import Image
from trainees_one.settings import BASE_DIR
import os


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )

        return user

    class Meta:
        model = User
        fields = ("id", "username", "password", "email",)


@celery_app.task(ignore_result=False)
def add_watermark_on_image(user_id, image_name):
    u = UserProfile.objects.get(user=user_id)
    original_image = Image.open(u.image)
    watermark = Image.open(os.path.join(BASE_DIR, 'media/watermark/index.jpeg'))
    original_image_x, original_image_y = original_image.size
    watermark_x, watermark_y = watermark.size
    scale = 10
    watermark_scale = max(original_image_x / (scale * watermark_x), original_image_y / (scale * watermark_y))
    new_size = (int(watermark_x * watermark_scale), int(watermark_y * watermark_scale))
    rgba_watermark = watermark.resize(new_size, resample=Image.ANTIALIAS)
    rgba_watermark_mask = rgba_watermark.convert("L").point(lambda x: min(x, 180))
    rgba_watermark.putalpha(rgba_watermark_mask)
    original_image.paste(rgba_watermark, (0, 0), rgba_watermark_mask)
    original_image.save(os.path.join(BASE_DIR, f'media/images/{image_name}'))
    u.image = f'images/{image_name}'
    u.save()


class UserProfileSerializer(ModelSerializer):
    long = DecimalField(write_only=True, required=False, max_digits=22, decimal_places=16)
    lat = DecimalField(write_only=True, required=False, max_digits=22, decimal_places=16)
    image = ImageField(required=False)
    first_name = CharField(source="user.first_name")
    last_name = CharField(source="user.last_name")

    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "gender", "image", "long", "lat")

    def update(self, instance, validated_data):
        image = validated_data.get('image', None)
        try:
            instance.user.first_name = validated_data['user']['first_name']
        except KeyError:
            pass
        try:
            instance.user.last_name = validated_data['user']['last_name']
        except KeyError:
            pass
        if image:
            add_watermark_on_image.delay(instance.id, str(validated_data['image']))
        instance.save()
        return instance


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        token['username'] = user.username
        return token


class RegisterUserSerializer(ModelSerializer):
    email = EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = CharField(write_only=True, required=True, validators=[validate_password])
    password2 = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

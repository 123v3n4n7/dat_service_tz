from rest_framework.serializers import ModelSerializer, DecimalField, CharField, EmailField, \
    ValidationError, ImageField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import *


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


class UserProfileSerializer(ModelSerializer):
    long = DecimalField(write_only=True, required=False, max_digits=22, decimal_places=16)
    lat = DecimalField(write_only=True, required=False, max_digits=22, decimal_places=16)
    image = ImageField(required=False)
    first_name = CharField(source="user.first_name")
    last_name = CharField(source="user.last_name")

    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "gender", "image", "long", "lat")


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

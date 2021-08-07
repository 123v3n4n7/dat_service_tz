from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from .models import UserProfile, MatchUsers
from .serializers import UserProfileSerializer, UserSerializer, MyTokenObtainPairSerializer, RegisterUserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User, AnonymousUser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from .permissions import IsAuthenticatedUpdateOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from .custom_filter import filter_queryset
from rest_framework.reverse import reverse
from .tasks import send_mail_if_match


class MatchUser(APIView):
    """Если был сделан get-запрос, то созадётся объект MatchUser, связывющий двух пользователей. Проверяется наличие
     взаимного объекта MatchUser, если такой есть, то вызывется функция send_mail_if_match."""

    def get(self, request, *args, **kwargs):
        try:
            user_id = kwargs['id']
            get_like_user = User.objects.get(id=user_id)
        except Exception:
            return Response({"User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if get_like_user == request.user:
            return Response(reverse('user_profiles-list'), status=status.HTTP_200_OK)
        obj, create = MatchUsers.objects.get_or_create(user_1=request.user, user_2=get_like_user)
        if create is True:
            try:
                MatchUsers.objects.get(user_1=get_like_user, user_2=request.user)
                email = UserSerializer(get_like_user).data['email']
                profile_1 = request.user
                profile_2 = get_like_user
                send_mail_if_match.delay(profile_1.email, profile_2.first_name, profile_2.last_name)
                send_mail_if_match.delay(profile_2.email, profile_1.first_name, profile_1.last_name)
                return Response({"email": email}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                pass
        return Response({"email": 'Like has been put'}, status=status.HTTP_200_OK)


class UserProfileList(viewsets.ModelViewSet):
    """Список профилей пользователей. Реализован фильтр по расстоянию, полу, имени и фамилии. Есть возможность
    посмотреть профиль пользователя. Если это профиль пользоваетя, под короым мы авторизовались, то можно
    внести изменения в профиль: указать долготу и широту, поменять изображение и т.д."""
    queryset = UserProfile.objects.prefetch_related('user').all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticatedUpdateOrReadOnly,)
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['gender']

    def get_queryset(self):
        """Фильтрация по расстоянию"""
        queryset = self.queryset
        if "distance" in self.request.query_params and type(self.request.user) is not AnonymousUser:
            user_profile = queryset.filter(user=self.request.user)[0]
            distance = self.request.query_params['distance']
            try:
                int(distance)
            except ValueError:
                return queryset
            queryset = filter_queryset(user_profile.lat, user_profile.long, queryset, distance). \
                exclude(user=self.request.user)
            return queryset
        else:
            return queryset


class RegisterUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterUserSerializer


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST)

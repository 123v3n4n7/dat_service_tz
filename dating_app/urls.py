from django.urls import path
from dating_app.views import MyObtainTokenPairView, RegisterUserView, LogoutView, MatchUser
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'dating_app'
urlpatterns = [
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create/', RegisterUserView.as_view(), name='auth_register'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path(r'clients/<id>/match/', MatchUser.as_view(), name='match_users')
]

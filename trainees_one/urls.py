from django.contrib import admin
from django.urls import path, include
from trainees_one import settings
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter
from dating_app.views import UserProfileList


router = SimpleRouter()
router.register(r'api/clients', UserProfileList, basename='user_profiles')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('dating_app.urls')),
]

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


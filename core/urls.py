from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.users.views import UserRegistrationView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth Endpoints
    path('api/auth/register/', UserRegistrationView.as_view(), name='signup'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("api/persona/", include("apps.persona.api.urls")),
    path("api/chat/", include("apps.chat.api.urls")),
    path("api/documents/", include("apps.documents.api.urls")),
    # Recommendation Endpoints
    # path('api/v1/recommendations/', include('apps.recommendations.urls')),

    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]



# Media files serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
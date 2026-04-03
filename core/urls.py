from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
  SpectacularAPIView,
  SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('education.urls')),

    path('api/v1/', SpectacularAPIView.as_view(), name='schema-v1'),
    path('api/v1/swagger/', SpectacularSwaggerView.as_view(url_name='schema-v1'), name='swagger-ui'),
]

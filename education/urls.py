from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParticipantViewSet

router = DefaultRouter()
router.register(r'employees', ParticipantViewSet, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
]
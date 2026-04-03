from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParticipantViewSet, CourseViewSet, CompanyViewSet, SpecificationViewSet

router = DefaultRouter()
router.register(r'employees', ParticipantViewSet, basename='employee')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'specification', SpecificationViewSet, basename='specification')
#router.register(r'courses', CourseViewSet, basename='course')
#router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
]
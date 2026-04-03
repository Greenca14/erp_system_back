from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'employees', ParticipantViewSet, basename='employee')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'specifications', SpecificationViewSet, basename='specification')
router.register(r'groups', StudyGroupViewSet, basename='group')

urlpatterns = [

    path('', include(router.urls)),

    path('groups/<int:group_id>/participants/', 
         GroupParticipantList.as_view(), name='group-participants-list'),
    
    path('groups/<int:group_id>/participants/<int:id>/', 
         GroupParticipantDetail.as_view(), name='group-participants-detail'),
]
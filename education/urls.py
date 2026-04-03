from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'specifications', SpecificationViewSet, basename='specification')
router.register(r'groups', GroupViewSet, basename='group')

urlpatterns = [
    path('xml/upload/', XMLUploadView.as_view(), name='xml-upload'),
    path('xml/export/<str:model_type>/<int:obj_id>/', XMLExportView.as_view(), name='xml-export'),
    
    path('', include(router.urls)),

    path('groups/<int:group_id>/employee/',
         GroupEmployeeViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='group-employee-list'),
    path('groups/<int:group_id>/employee/<int:id>/',
         GroupEmployeeViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}),
         name='group-employee-detail'),
]
from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import Participant, Course
from .serializers import ParticipantSerializer, CourseSerializer
class ParticipantViewSet(viewsets.ModelViewSet):
    """
    CRUD для сотрудников.
    """
    queryset = Participant.objects.all().select_related('company')
    serializer_class = ParticipantSerializer
    
    # Добавим поиск и фильтрацию  XDDD
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'email'] 
    ordering_fields = ['id', 'full_name']  


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD для Курсов обучения (п. 2.2.2).
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    # Поиск по названию курса пригодится для фронтенда
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
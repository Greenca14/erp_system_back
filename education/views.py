from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import Participant
from .serializers import ParticipantSerializer

class ParticipantViewSet(viewsets.ModelViewSet):
    """
    CRUD для сотрудников (Участников обучения).
    Реализует методы: list, create, retrieve, update, destroy.
    """
    queryset = Participant.objects.all().select_related('company')
    serializer_class = ParticipantSerializer
    
    # Добавим поиск и фильтрацию для удобства фронтенда XDDD
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'email'] # Поиск по ФИО и почте
    ordering_fields = ['id', 'full_name']  # Сортировка
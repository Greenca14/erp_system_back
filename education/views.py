from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import Participant, Course, Company, Specification
from .serializers import ParticipantSerializer, CourseSerializer, CompanySerializer, SpecificationSerializer

class ParticipantViewSet(viewsets.ModelViewSet):
    """
    CRUD для Сотрудников (п. 2.2.1).
    """
    queryset = Participant.objects.all().select_related('company')
    serializer_class = ParticipantSerializer
    
    # Добавим поиск и фильтрацию  XDDD
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'email'] 
    ordering_fields = ['id', 'full_name']  


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD для Курсов (п. 2.2.2).
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

class CompanyViewSet(viewsets.ModelViewSet):
    """
    CRUD для Компаний (п. 2.2.6).
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name']

class SpecificationViewSet(viewsets.ModelViewSet):
    """
    CRUD для Спецификаций (п. 2.2.5).
    """
    queryset = Specification.objects.all().select_related('company').prefetch_related('study_groups__course')
    serializer_class = SpecificationSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['number', 'company__name']
from django.shortcuts import render
from rest_framework import viewsets, status
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class ParticipantViewSet(viewsets.ModelViewSet):
    """
    CRUD для Сотрудников (п. 2.2.1).
    """
    queryset = Participant.objects.all().select_related('company')
    serializer_class = ParticipantSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD для Курсов (п. 2.2.2).
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """
    CRUD для Компаний (п. 2.2.6).
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class SpecificationViewSet(viewsets.ModelViewSet):
    """
    CRUD для Спецификаций (п. 2.2.5).
    """
    queryset = Specification.objects.all().select_related('company').prefetch_related('groups__course')
    serializer_class = SpecificationSerializer


class StudyGroupViewSet(viewsets.ModelViewSet):
    """
    CRUD для Спецификаций (п. 2.2.3).
    """
    queryset = StudyGroup.objects.select_related('course').all()
    serializer_class = StudyGroupSerializer


class GroupParticipantList(APIView):
    def get(self, request, group_id):
        participants = GroupParticipant.objects.filter(group_id=group_id)
        serializer = GroupParticipantSerializer(participants, many=True)
        return Response(serializer.data)

    def post(self, request, group_id):
        group = get_object_or_404(StudyGroup, id=group_id)
        serializer = GroupParticipantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(group=group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupParticipantDetail(APIView):
    def patch(self, request, group_id, id):
        entry = get_object_or_404(GroupParticipant, id=id, group_id=group_id)
        serializer = GroupParticipantSerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, group_id, id):
        entry = get_object_or_404(GroupParticipant, id=id, group_id=group_id)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
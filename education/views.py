import threading
from django.shortcuts import render
from rest_framework import viewsets, status
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from .services import run_xml_import, export_employee_to_xml, export_course_to_xml
from django.http import HttpResponse

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().select_related('company')
    serializer_class = EmployeeSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class SpecificationViewSet(viewsets.ModelViewSet):
    queryset = Specification.objects.all().select_related('company')
    serializer_class = SpecificationSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().select_related('course').select_related('specification')
    serializer_class = GroupSerializer


class GroupEmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = GroupEmployeeSerializer

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        if group_id:
            return GroupEmployee.objects.filter(group_id=group_id)
        return GroupEmployee.objects.none()

    def get_object(self):
        group_id = self.kwargs.get('group_id')
        employee_id = self.kwargs.get('id')
        if group_id and employee_id:
            return get_object_or_404(GroupEmployee, group_id=group_id, employee_id=employee_id)
        return super().get_object()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(Group, pk=group_id)
        employee_ids = request.data.get('employee_ids', [])

        if not isinstance(employee_ids, list):
            return Response(
                {"error": "employee_ids должен быть списком ID"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        errors = []
        for emp_id in employee_ids:
            try:
                employee = Employee.objects.get(pk=emp_id)
                membership, created_flag = GroupEmployee.objects.get_or_create(
                    group=group, employee=employee
                )
                if created_flag:
                    created.append(employee.id)
            except Employee.DoesNotExist:
                errors.append(f"Employee {emp_id} not found")

        return Response(
            {"created": created, "errors": errors},
            status=status.HTTP_201_CREATED
        )

    # PATCH /groups/<group_id>/employee/<id>/  → update membership (e.g. role)
    def partial_update(self, request, *args, **kwargs):
        membership = self.get_object()
        serializer = self.get_serializer(membership, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # DELETE /groups/<group_id>/employee/<id>/  → remove employee from group
    def destroy(self, request, *args, **kwargs):
        membership = self.get_object()
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class XMLUploadView(APIView):
    """
    API для асинхронной загрузки данных из Global ERP через XML.
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response(
                {"error": "Файл не найден. Используйте ключ 'file' в form-data."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Минимальная валидация
        if not file_obj.name.endswith('.xml'):
            return Response({"error": "Допускаются только XML файлы."}, status=400)

        try:
            # Читаем контент сразу
            file_content = file_obj.read()
            
            # Асинхронный запуск 
            thread = threading.Thread(target=run_xml_import, args=(file_content,))
            thread.daemon = True
            thread.start()
            
            return Response({
                "status": "success",
                "message": f"Файл {file_obj.name} принят и обрабатывается в фоне."
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            return Response({"error": f"Ошибка сервера: {str(e)}"}, status=500)
        
class XMLExportView(APIView):
    """API для выгрузки XML данных"""
    
    def get(self, request, model_type, obj_id):
        try:
            if model_type == 'employee':
                xml_data = export_employee_to_xml(obj_id)
                filename = f"employee_{obj_id}.xml"
            elif model_type == 'course':
                xml_data = export_course_to_xml(obj_id)
                filename = f"course_{obj_id}.xml"
            else:
                return HttpResponse("Неверный тип модели", status=400)

            response = HttpResponse(xml_data, content_type='application/xml')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            return HttpResponse(f"Ошибка при экспорте: {str(e)}", status=404)
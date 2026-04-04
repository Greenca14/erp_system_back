import threading
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, inline_serializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.generics import GenericAPIView
from rest_framework import viewsets, status, filters
from rest_framework.pagination import PageNumberPagination
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from .services import run_xml_import, export_employee_to_xml, export_course_to_xml
from django.http import HttpResponse
from datetime import timedelta
from django.db.models import Min, Max, Avg

class StandardSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'per_page'
    max_page_size = 100


@extend_schema(
    tags=['Участник обучения - Employee']
)
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().select_related('company')
    serializer_class = EmployeeSerializer
    pagination_class = StandardSetPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'email']
    ordering_fields = ['id', 'full_name']

@extend_schema(
    tags=['Курс обучения - Course'],
)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardSetPagination

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

@extend_schema(
    tags=['Компания - Company']
)
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = StandardSetPagination
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']


@extend_schema(
    tags=['Спецификация - Specification']
)
class SpecificationViewSet(viewsets.ModelViewSet):
    queryset = Specification.objects.all().select_related('company')
    serializer_class = SpecificationSerializer
    pagination_class = StandardSetPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['company', 'date']
    search_fields = ['number', 'company__name']
    ordering_fields = ['id', 'date', 'number', 'total_with_vat']
    

@extend_schema(
    tags=['Учебная группа - Group']
)
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().select_related('course').select_related('specification')
    serializer_class = GroupSerializer
    pagination_class = StandardSetPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['status', 'course', 'specification']
    search_fields = ['course__title', 'specification__number']
    ordering_fields = ['id', 'start_date', 'end_date', 'status', 'average_progress']

@extend_schema(
    tags=['Участники группы - Group Employees']
)
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

    @extend_schema(
        description='Вывод всех пользователей принадлежащих к группе'
    )
    def list(self, request, *args, **kwargs):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(Group, pk=group_id)

        memberships = self.get_queryset()
        group_serializer = SimpleGroupSerializer(group)

        employees_data = []
        for membership in memberships:
            emp_data = SimpleEmployeeSerializer(membership.employee).data
            emp_data['progress_percent'] = membership.progress_percent
            employees_data.append(emp_data)

        return Response({
            "group": group_serializer.data,
            "employees": employees_data
        })

    @extend_schema(
        description='Добавить пользователей в группу',
        request=inline_serializer(
            name='AddEmployeesRequest',
            fields={
                'employee_ids': serializers.ListField(
                    child=serializers.IntegerField(),
                    help_text='Список ID сотрудников для добавления в группу'
                ),
            }
        ),
        responses={
            201: inline_serializer(
                name='AddEmployeesResponse',
                fields={
                    'created': serializers.ListField(child=serializers.IntegerField()),
                    'errors': serializers.ListField(child=serializers.CharField()),
                }
            ),
            400: inline_serializer(
                name='BadRequestResponse',
                fields={'error': serializers.CharField()}
            ),
        }
    )
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

    @extend_schema(
        description='Обновить прогресс пользователя',
        request=inline_serializer(
            name='UpdateProgressRequest',
            fields={
                'progress_percent': serializers.IntegerField(
                    min_value=0, max_value=100,
                    help_text='Новый прогресс (0-100)'
                )
            }
        ),
        responses={
            200: GroupEmployeeSerializer(),
            404: None,
        }
    )
    def partial_update(self, request, *args, **kwargs):
        membership = self.get_object()
        serializer = self.get_serializer(membership, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @extend_schema(
        description='Удалить пользователя из группы'
    )
    def destroy(self, request, *args, **kwargs):
        membership = self.get_object()
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Импорт и экспорт в формате XML'],
    request=XMLUploadSerializer,
    responses={
        202: inline_serializer(
            name='XMLUploadResponse',
            fields={
                'status': serializers.CharField(),
                'message': serializers.CharField(),
            }
        ),
        400: inline_serializer(
            name='XMLUploadError',
            fields={'error': serializers.CharField()}
        ),
    }
)
class XMLUploadView(APIView):
    """
    API для асинхронной загрузки данных из Global ERP через XML.
    """
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = XMLUploadSerializer

    def post(self, request):
        serializer = XMLUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file_obj = serializer.validated_data['file']
        
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


@extend_schema(
    tags=['Импорт и экспорт в формате XML']
)
class XMLExportView(GenericAPIView):
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


@extend_schema(
    tags=['Данные для диаграммы Ганта']
)
class GanttChartDataView(APIView):

    def get(self, request):
        groups_qs = Group.objects.all()
        
        if not groups_qs.exists():
            return Response({
                "min_date": None,
                "max_date": None,
                "groups": []
            })

        aggr = groups_qs.aggregate(
            first_start=Min('start_date'),
            last_end=Max('end_date')
        )

        min_date = aggr['first_start'] - timedelta(days=3) if aggr['first_start'] else None
        max_date = aggr['last_end'] + timedelta(days=3) if aggr['last_end'] else None

        serializer = SimpleGroupSerializer(groups_qs, many=True)

        return Response({
            "min_date": min_date,
            "max_date": max_date,
            "groups": serializer.data
        })
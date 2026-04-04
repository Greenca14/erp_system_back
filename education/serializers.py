from typing import Any, Dict, List

from rest_framework import serializers
from .models import Employee, Company, Course, Specification, Group, GroupEmployee

class SimpleSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['id', 'date', 'number']


class SimpleEmployeeSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source='company.name', read_only=True, help_text='Наименование компании'
    )

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'company_name', 'email']


class SimpleGroupSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source='course.title', read_only=True, help_text='Наименование курса'
    )

    class Meta:
        model = Group
        fields = ['id', 'course_title', 'start_date', 'end_date', 'status', 'average_progress']


class SimpleGroupSerializerWithMembers(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source='course.title', read_only=True, help_text='Наименование курса'
    )
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'course_title', 'start_date', 'end_date', 'status', 'average_progress', 'members']

    def get_members(self, obj) -> List[Dict[str, Any]]:
        memberships = obj.group_membership.select_related('employee').all()
        return SimpleEmployeeSerializer([m.employee for m in memberships], many=True).data


class SimpleCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'code', 'name']


class CompanySerializer(serializers.ModelSerializer):
    specifications = SimpleSpecificationSerializer(
        read_only=True, many=True, help_text='Спецификации компании'
    )

    class Meta:
        model = Company
        fields = [
            'id',
            'code',
            'name',
            'specifications'
        ]

    def validate_code(self, value):
        """Проверка длины кода (2.2.6.2)"""
        if not (2 <= len(value) <= 4):
            raise serializers.ValidationError("Код компании должен содержать от 2 до 4 символов.")
        
        qs = Company.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Компания с таким кодом уже существует.")
        
        return value.upper()
    

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',            
            'title',        
            'description',   
            'duration_days', 
            'base_price'     
        ]
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True}
        }


class GroupSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True, help_text='Курс')
    specification = SimpleSpecificationSerializer(read_only=True, help_text='Спецификация')

    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True, source='course',
        help_text='ID курса'
    )
    specification_id = serializers.PrimaryKeyRelatedField(
        queryset=Specification.objects.all(), write_only=True, source='specification',
        help_text='ID спецификации'
    )

    class Meta:
        model = Group
        fields = [
            'id',
            'course',
            'course_id',
            'specification',
            'specification_id',
            'start_date',
            'end_date',
            'price_at_creation',
            'status',
            'total_cost',
            'employees_count',
            'average_progress',
        ]
        extra_kwargs = {
            'price_at_creation': {'default': 0, 'read_only': True},
            'total_cost': {'default': 0, 'read_only': True},
        }


class EmployeeSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    groups = SimpleGroupSerializer(source='enrolled_groups', read_only=True, many=True)
    
    assign_to_groups = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False,
        help_text='Список ID групп, к которым пользователь присоединится после обновления/добавления записи'
    )

    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), write_only=True, source='company',
        help_text='ID компании'
    )

    class Meta:
        model = Employee
        fields = [
            'id',
            'full_name',
            'company',
            'company_id',
            'email',
            'groups',
            'assign_to_groups'
        ]

    def validate_email(self, value):
        existing = Employee.objects.filter(email=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError("Сотрудник с таким Email уже существует.")
        return value
        
    def _handle_group_assignments(self, employee, group_ids):
        if not group_ids:
            return
        for group_id in group_ids:
            try:
                group = Group.objects.get(id=group_id)
                GroupEmployee.objects.get_or_create(
                    employee=employee,
                    group=group,
                )
            except Group.DoesNotExist:
                print(f"Группа с ID {group_id} не найдена.")

    def create(self, validated_data):
        group_ids = validated_data.pop('assign_to_groups', [])
        employee = Employee.objects.create(**validated_data)
        
        if group_ids is not None:
            self._handle_group_assignments(employee, group_ids)
        
        return employee

    def update(self, instance, validated_data):
        group_ids = validated_data.pop('assign_to_groups', None)
        employee = super().update(instance, validated_data)

        if group_ids is not None:
            self._handle_group_assignments(employee, group_ids)

        return employee


class SpecificationSerializer(serializers.ModelSerializer):
    number = serializers.CharField(
        read_only=True, help_text='Номер спецификации', required=False
    )

    company = SimpleCompanySerializer(read_only=True, help_text='Компания')
    groups = SimpleGroupSerializer(many=True, read_only=True, help_text='Группа')
    
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), write_only=True, source='company',
        help_text='ID компании за которой будет закреплена специализация'
    )

    class Meta:
        model = Specification
        fields = [
            'id',
            'date',
            'number',
            'company',
            'company_id',
            'groups',
            'total_no_vat',
            'vat_amount',
            'total_with_vat'
        ]


class GroupEmployeeSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), write_only=True, source='employee',
        help_text='ID работника, который будет обновлен/удален'
    )
    employee = SimpleEmployeeSerializer(
        read_only=True, help_text='Работник'
    )
    group = SimpleGroupSerializer(
        read_only=True, help_text='Группа'
    )

    class Meta:
        model = GroupEmployee
        fields = [
            'id', 
            'group',
            'employee',
            'employee_id',
            'progress_percent'
        ]


class XMLUploadSerializer(serializers.Serializer):
    file = serializers.FileField(help_text="Выберите XML файл для импорта.")
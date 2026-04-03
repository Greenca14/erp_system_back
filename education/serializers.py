from rest_framework import serializers
from .models import Participant, Company, Course, Specification, StudyGroup
from decimal import Decimal

class ParticipantSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')

    learning_groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='course__title', source='group_participants')

    class Meta:
        model = Participant
        fields = [
            'id',
            'full_name',
            'company',
            'company_name',
            'email',
            'learning_groups'
        ]

    def validate_email(self, value):
        existing = Participant.objects.filter(email=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError("Сотрудник с таким Email уже существует.")
        return value
    

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',            # 1. CourseID
            'title',         # 2. Название курса
            'description',   # 3. Описание курса
            'duration_days', # 4. Длительность в днях
            'base_price'     # 5. Цена за человека
        ]
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True}
        }


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',            # 1. CourseID
            'code',         # 2. Код компании
            'name',   # 3. Полное название
        ]

        def validate_code(self, value):
            """Проверка длины кода (п. 2.2.6.2 )"""
            if not (2 <= len(value) <= 4):
                raise serializers.ValidationError("Код компании должен содержать от 2 до 4 символов.")
            return value.upper()

class StudyGroupSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True, source='course'
    )

    class Meta:
        model = StudyGroup
        fields = [
            'id',
            'course',
            'course_id',
            'start_date',
            'end_date',
            'participants_count',
            'average_progress',
            'total_cost',
        ]

class SpecificationSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    groups = StudyGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Specification
        fields = [
            'id',
            'date',
            'number',
            'company',
            'groups',
            'total_no_vat',
            'vat_amount',
            'total_with_vat'
        ]
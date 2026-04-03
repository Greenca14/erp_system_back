from rest_framework import serializers
from .models import Employee, Company, Course, Specification, StudyGroup, GroupParticipant
from decimal import Decimal


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',        
            'code',       
            'name',
        ]

    def validate_code(self, value):
        """Проверка длины кода (п. 2.2.6.2 )"""
        if not (2 <= len(value) <= 4):
            raise serializers.ValidationError("Код компании должен содержать от 2 до 4 символов.")
        return value.upper()
    

class ParticipantSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    groups = serializers.SerializerMethodField()
    
    assign_to_groups = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    company_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'full_name',
            'email',
            'company',
            'groups',
            'assign_to_groups',
            'company_id'
        ]

    def validate_email(self, value):
        existing = Employee.objects.filter(email=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError("Сотрудник с таким Email уже существует.")
        return value
    
    def get_groups(self, participant):
        group_participations = GroupParticipant.objects.filter(participant=participant)
        groups = [gp.group for gp in group_participations]
        serializer = StudyGroupSerializer(groups, many=True)
        return serializer.data
        
    def _handle_group_assignments(self, participant, group_ids):
        if not group_ids:
            return

        for group_id in group_ids:
            try:
                group = StudyGroup.objects.get(id=group_id)
                GroupParticipant.objects.get_or_create(
                    participant=participant,
                    group=group,
                )
            except StudyGroup.DoesNotExist:
                print(f"Группа с ID {group_id} не найдена.")

    def create(self, validated_data):
        group_ids = validated_data.pop('assign_to_groups', [])
        participant = Employee.objects.create(**validated_data)
        
        if group_ids is not None:
            self._handle_group_assignments(participant, group_ids)
        
        return participant

    def update(self, instance, validated_data):
        group_ids = validated_data.pop('assign_to_groups', None)
        participant = super().update(instance, validated_data)

        if group_ids is not None:
            self._handle_group_assignments(participant, group_ids)

        return participant
    

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


class SpecificationShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = [
            'id',
            'date',
            'number',
        ]


class StudyGroupSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    specification = SpecificationShortSerializer(read_only=True)

    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True, source='course'
    )
    specification_id = serializers.PrimaryKeyRelatedField(
        queryset=Specification.objects.all(), write_only=True, source='specification'
    )

    class Meta:
        model = StudyGroup
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


class GroupParticipantSerializer(serializers.ModelSerializer):
    participant = ParticipantSerializer(read_only=True)

    class Meta:
        model = GroupParticipant
        fields = [
            'id', 
            'participant',
            'progress_percent'
        ]
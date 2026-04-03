from rest_framework import serializers
from .models import Participant, Company, Course, Specification, StudyGroup, GroupParticipant
from decimal import Decimal

class ParticipantSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')

    groups = serializers.SerializerMethodField()
    
    assign_to_groups = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Participant
        fields = [
            'id',
            'full_name',
            'email',
            'company',
            'groups',
            'assign_to_groups'
        ]

    def validate_email(self, value):
        existing = Participant.objects.filter(email=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise serializers.ValidationError("Сотрудник с таким Email уже существует.")
        return value
    
    def get_groups(self, participant):
        group_participations = GroupParticipant.objects.filter(participant=participant)
        return group_participations
        
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

class GroupParticipantSerializer(serializers.ModelSerializer):
    class Meta:
            model = GroupParticipant
            fields = [
                'id',
                'group',
                'participant',
                'progress_percent',
            ]
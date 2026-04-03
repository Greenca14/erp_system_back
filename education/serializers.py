from rest_framework import serializers
from .models import Participant, Company, Course

class ParticipantSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')

    learning_groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='course__title', source='group_participants')

    class Meta:
        model = Participant
        fields = [
            'id',               # 1. EmployeeID
            'full_name',        # 2. ФИО
            'company',          # 3. Компания (ID для записи)
            'company_name',     # 3. Компания (Название для чтения)
            'email',            # 4. Email
            'learning_groups'   # 5. Группы обучения
        ]

    def validate_email(self, value):
        """Проверка на дубли (п. 2.2.1)"""
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
            'price_per_person' # 5. Цена за человека
        ]
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True}
        }


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
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
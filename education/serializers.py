from rest_framework import serializers
from .models import Participant, Company, Course, Specification, StudyGroup
from decimal import Decimal

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
        
class SpecificationSerializer(serializers.ModelSerializer):
    
    company_name = serializers.ReadOnlyField(source='company.name')

    group_info = serializers.SerializerMethodField()

    total_amount_no_vat = serializers.SerializerMethodField()
    vat_amount = serializers.SerializerMethodField()
    total_with_vat = serializers.SerializerMethodField()

    class Meta:
        model = Specification
        fields = [
            'id',                   # 1. DocumentID
            'date',                 # 2. Дата
            'number',               # 3. Номер
            'company',              # 4. Компания (ID)
            'company_name',         # 4. Название компании
            'study_groups',         # 5. Группы (ID для записи)
            'group_numbers',        # 5. Номера групп (для чтения)
            'total_amount_no_vat',  # 6. Сумма без НДС
            'vat_amount',           # 7. НДС (22%)
            'total_with_vat'        # 8. Итого с НДС
        ]

    def get_group_info(self, obj):
        return [group.course.title for group in obj.study_groups.all()]

    def get_total_amount_no_vat(self, obj):
        total = sum(group.total_group_cost for group in obj.study_groups.all())
        return round(total, 2)

    def get_vat_amount(self, obj):
        total_no_vat = Decimal(str(self.get_total_amount_no_vat(obj)))
        vat = total_no_vat * Decimal('0.22')
        return round(vat, 2)

    def get_total_with_vat(self, obj):
        total_no_vat = Decimal(str(self.get_total_amount_no_vat(obj)))
        vat = Decimal(str(self.get_vat_amount(obj)))
        return round(total_no_vat + vat, 2)
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, Avg

class Company(models.Model):
    """2.2.6 Компания"""
    code = models.CharField(max_length=4, unique=True, verbose_name="Код компании")
    name = models.CharField(max_length=255, verbose_name="Полное наименование")

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return f"{self.code} | {self.name}"


class Course(models.Model):
    """2.2.2 Kypc обучения"""
    title = models.CharField(max_length=255, verbose_name="Название курса")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    duration_days = models.PositiveIntegerField(verbose_name="Длительность (дни)")
    base_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена за чел. (руб)")

    class Meta:
        verbose_name = "Kypc обучения"
        verbose_name_plural = "Курсы обучения"

    def __str__(self):
        return self.title

class Specification(models.Model):
    """2.2.5 Спецификация"""
    date = models.DateField(verbose_name="Дата спецификации")
    number = models.CharField(max_length=50, unique=True, verbose_name="Номер спецификации")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='specifications', verbose_name="Компания-заказчик")

    @property
    def total_no_vat(self):
        """Сумма всех групп без НДС (2.2.5.6)"""
        return self.groups.aggregate(total=Sum('total_cost'))['total'] or 0

    @property
    def vat_amount(self):
        """НДС 22% (2.2.5.7)"""
        return float(self.total_no_vat) * 0.22

    @property
    def total_with_vat(self):
        """Итого с НДС (2.2.5.8)"""
        return float(self.total_no_vat) + self.vat_amount

    class Meta:
        verbose_name = "Спецификация"
        verbose_name_plural = "Спецификации"

    def __str__(self):
        return f"Спец. №{self.number} от {self.date}"

class Group(models.Model):
    """2.2.3 Учебная группа"""
    STATUS_CHOICES = [
        ('planned', 'Планируется'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершено'),
    ]

    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='groups', verbose_name="Kypc")
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE, related_name='groups', verbose_name="Спецификация")
    employees = models.ManyToManyField('Employee', related_name='enrolled_groups', through='GroupEmployee')
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    
    # Фиксация цены на момент создания
    price_at_creation = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена за чел. на момент записи")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned', verbose_name="Статус")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Стоимость за группу")

    @property
    def employees_count(self):
        return self.group_membership.count()

    
    @property
    def average_progress(self):
        """Расчет среднего прогресса обучения по группе"""
        return self.group_membership.aggregate(avg=Avg('progress_percent'))['avg'] or 0

    def save(self, *args, **kwargs):
        if not self.price_at_creation:
            self.price_at_creation = self.course.base_price
        
        if self.pk:
            self.total_cost = self.price_at_creation * self.employees_count
        else:
            self.total_cost = 0
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Учебная группа"
        verbose_name_plural = "Учебные группы"


class Employee(models.Model):
    """2.2.1 Участник обучения"""
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees', verbose_name="Компания")
    email = models.EmailField(unique=True, verbose_name="Email")

    class Meta:
        verbose_name = "Участник обучения"
        verbose_name_plural = "Участники обучения"

    def __str__(self):
        return self.full_name


class GroupEmployee(models.Model):
    """2.2.4 Участник группы"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_membership', verbose_name="Группа")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_membership', verbose_name="Сотрудник")
    progress_percent = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Прогресс (%)"
    )

    class Meta:
        unique_together = ('group', 'employee')
        verbose_name = "Участник группы"
        verbose_name_plural = "Детализация групп"

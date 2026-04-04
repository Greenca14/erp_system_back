import factory
from factory.django import DjangoModelFactory
from faker import Faker
from datetime import timedelta
from .models import Company, Course, Specification, Group, Employee, GroupEmployee

fake = Faker()

class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company
        django_get_or_create = ('code',)

    code = factory.LazyAttribute(lambda _: fake.unique.bothify(text='??##').upper())
    name = factory.Faker('company')


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course
        django_get_or_create = ('title',)

    title = factory.Faker('catch_phrase')
    description = factory.Faker('text', max_nb_chars=200)
    duration_days = factory.Faker('random_int', min=5, max=25)
    base_price = factory.Faker('random_int', min=500, max=10000)


class SpecificationFactory(DjangoModelFactory):
    class Meta:
        model = Specification
        django_get_or_create = ('number',)

    date = factory.Faker('date_this_year')
    number = factory.Sequence(lambda n: f"SP-{n:04d}") 
    company = factory.SubFactory(CompanyFactory)


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ('course', 'specification', 'start_date')

    course = factory.SubFactory(CourseFactory)
    specification = factory.SubFactory(SpecificationFactory)
    start_date = factory.Faker('date_this_year')
    end_date = factory.LazyAttribute(
        lambda obj: obj.start_date + timedelta(days=obj.course.duration_days)
    )
    price_at_creation = factory.LazyAttribute(lambda obj: obj.course.base_price)
    status = factory.Iterator(['planned', 'in_progress', 'completed'])
    total_cost = 0

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = model_class(*args, **kwargs)
        instance.save()
        return instance


class EmployeeFactory(DjangoModelFactory):
    class Meta:
        model = Employee
        django_get_or_create = ('email',)

    full_name = factory.Faker('name')
    company = factory.SubFactory(CompanyFactory)
    email = factory.LazyAttribute(lambda obj: fake.unique.email())


class GroupEmployeeFactory(DjangoModelFactory):
    class Meta:
        model = GroupEmployee
        django_get_or_create = ('group', 'employee')

    group = factory.SubFactory(GroupFactory)
    employee = factory.SubFactory(EmployeeFactory)
    progress_percent = factory.Faker('random_int', min=0, max=100)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = super()._create(model_class, *args, **kwargs)
        instance.group.save()
        return instance
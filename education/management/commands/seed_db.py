# education/management/commands/seed_db.py
import random

from django.core.management.base import BaseCommand
import factory
from education.factories import (
    CompanyFactory, CourseFactory, SpecificationFactory,
    GroupFactory, EmployeeFactory, GroupEmployeeFactory
)

class Command(BaseCommand):
    help = 'Заполнить базу данных тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Генерация компаний...')
        companies = CompanyFactory.create_batch(3)

        self.stdout.write('Генерация учебных курсов...')
        courses = CourseFactory.create_batch(5)

        self.stdout.write('Генерация спецификаций...')
        specs = [SpecificationFactory(company=company) for company in companies for _ in range(2)]

        self.stdout.write('Генерация учебных групп...')
        groups = GroupFactory.create_batch(10, specification=factory.Iterator(specs))

        self.stdout.write('Генерация участников групп...')
        employees = []
        for company in companies:
            employees.extend(EmployeeFactory.create_batch(10, company=company))

        self.stdout.write('Генерация связей...')
        for group in groups:
            chosen = random.sample(employees, k=random.randint(3, 5))
            for emp in chosen:
                GroupEmployeeFactory(group=group, employee=emp)

        self.stdout.write(self.style.SUCCESS('База данных заполнена успешно!'))
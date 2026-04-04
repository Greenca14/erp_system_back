from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = 'Очистить записи в базе данных'

    def handle(self, *args, **options):
        with transaction.atomic():
            deletion_order = [
                apps.get_model('education', 'GroupEmployee'),
                apps.get_model('education', 'Group'),
                apps.get_model('education', 'Specification'),
                apps.get_model('education', 'Employee'),
                apps.get_model('education', 'Course'),
                apps.get_model('education', 'Company'),
            ]

            for model in deletion_order:
                count = model.objects.all().delete()[0]
                if count:
                    self.stdout.write(f"Удалено {count} записей {model.__name__}")

            self.reset_sequences(deletion_order)

        self.stdout.write(self.style.SUCCESS("Database cleared successfully!"))

    def reset_sequences(self, models_to_clear):
        db_vendor = connection.vendor

        for model in models_to_clear:
            table_name = model._meta.db_table

            if db_vendor == 'sqlite':
                with connection.cursor() as cursor:
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = %s", [table_name])
            else:
                self.stdout.write(f"Сброс автоинкремента индексов не удался, доступно только для СУБД Sqlite.")
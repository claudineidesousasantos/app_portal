from django.core.management.base import BaseCommand
from barbershop_management.models import DayOfWeek, Barbershop

class Command(BaseCommand):
    help = 'Populate days of week'

    def handle(self, *args, **options):
        for day_number, day_name in Barbershop.DAYS_OF_WEEK:
            DayOfWeek.objects.get_or_create(day=day_number, name=day_name)
        self.stdout.write(self.style.SUCCESS('Successfully populated days of week'))

from django.core.management.base import BaseCommand, CommandError
from backend.models import Unit


class Command(BaseCommand):
    help = "Bootstrap Units"

    # def add_arguments(self, parser):

    def handle(self, *args, **options):
        try:
            status = Unit.objects.get_or_create(
                name = 'Sky View',
                type = 'Penthouse',
                number_of_rooms = 3,
                number_of_bathrooms = 3,
                price = 200,
                occupancy = 6,
                breakfast = True,
                breakfast_price = 30,
                active = True
            )
            self.stdout.write(
                self.style.SUCCESS('Operation successful: %s' % str(status))
            )

            status = Unit.objects.get_or_create(
                name = 'Sky Serenity',
                type = 'Apartment',
                number_of_rooms = 2,
                number_of_bathrooms = 1,
                price = 150,
                occupancy = 4,
                breakfast = True,
                breakfast_price = 30,
                active = True
            )
            self.stdout.write(
                self.style.SUCCESS('Operation successful: %s' % str(status))
            )
        except Exception as e:
            raise CommandError(e)

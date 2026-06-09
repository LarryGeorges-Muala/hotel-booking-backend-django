from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.conf import settings
from backend.models import Unit


class Command(BaseCommand):
    help = "Bootstrap Units"

    # def add_arguments(self, parser):

    def handle(self, *args, **options):
        try:
            penthouse = Unit.objects.create(
                pk = (Unit.objects.count() + 1),
                name = 'View',
                type = 'Penthouse',
                price = 200,
                occupancy = 6,
                breakfast = True,
                breakfast_price = 30,
                active = True
            )
            penthouse.unitphoto_set.create(
                unit = penthouse,
                display = True,
                thumbnail = True,
                name = penthouse.name,
                description = '{} Thumbnail'.format(penthouse.name),
                category = 'Living',
                image = 'demo/thumbnail/thumbnail.jpg'
            )
            bedroom = penthouse.bedroom_set.create(
                unit = penthouse,
                master_bedroom = True,
                bed_type = 'King',
                number_of_beds = 1
            )
            penthouse.bedroomphoto_set.create(
                unit = penthouse,
                bedroom = bedroom,
                display = True,
                name = penthouse.name,
                description = '{} Bedroom'.format(penthouse.name),
                image = 'demo/room/bedroom.jpg'
            )
            bathroom = penthouse.bathroom_set.create(
                unit = penthouse,
                bathroom_type = 'Full'
            )
            penthouse.bathroomphoto_set.create(
                unit = penthouse,
                bathroom = bathroom,
                display = True,
                name = penthouse.name,
                description = '{} Bathroom'.format(penthouse.name),
                image = 'demo/bathroom/bathroom.jpg'
            )
            penthouse.save()
            self.stdout.write(
                self.style.SUCCESS('Operation successful: %s' % str(penthouse))
            )
        except Exception as e:
            raise CommandError(e)

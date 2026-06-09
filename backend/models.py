import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from common import _rabbitmq_modules
from . import _booking_modules


class Client(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    ip = models.GenericIPAddressField(null=True, blank=True)
    title = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=254, default='')
    phone = models.CharField(max_length=200, blank=True)
    created_date = models.DateTimeField("created", default=timezone.now)
    last_updated = models.DateTimeField("last updated", default=timezone.now)

    def __str__(self):
        return f"{self.id} - {self.user.username}"

    def was_published_recently(self):
        return self.created_date >= timezone.now() - datetime.timedelta(days=1)

    def save(self, *args, **kwargs):
        # Refresh update timestamp
        self.last_updated = timezone.now()
        # Save
        super().save(*args, **kwargs)


class Unit(models.Model):

    # Limit choices
    UNIT_TYPE_CHOICES = [
        ('Apartment', 'Apartment'),
        ('Penthouse', 'Penthouse'),
        ('Villa', 'Villa'),
    ]

    # Upload path
    def generate_upload_path(self, instance):
        unit_name = str(self.name).replace(" ", "-")
        upload_path = "uploads/{}/thumbnails/{}".format(
            str(unit_name).lower(), instance
        )
        return upload_path

    # Fields
    name = models.CharField(max_length=200)
    type = models.CharField(
        max_length=200,
        choices=UNIT_TYPE_CHOICES,
        default='Apartment',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    occupancy = models.IntegerField(
        validators=[
            MinValueValidator(1)
        ],
        default=1
    )
    breakfast = models.BooleanField(default=True)
    breakfast_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    thumbnail = models.CharField(max_length=200, default='')
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField("created", default=timezone.now)
    last_updated = models.DateTimeField("last updated", default=timezone.now)

    def __str__(self):
        return f"{self.id} - {self.name}"

    def was_published_recently(self):
        return self.created_date >= timezone.now() - datetime.timedelta(days=1)

    def number_of_rooms_in_unit(self):
        return self.bedroom_set.count()

    def number_of_bathrooms_in_unit(self):
        return (self.bathroom_set.filter(bathroom_type="Full").count() * 1) + (self.bathroom_set.filter(bathroom_type="Half").count() * 0.5)
    
    def activable(self):
        if (self.number_of_rooms_in_unit() >= 1) and (self.number_of_bathrooms_in_unit() >= 0.5):
            return True
        return False

    def generate_unit_photos(self):
        entries_list = []
        albums = self.unitphoto_set.filter(display=True)
        if not albums:
            entries_list.append({
                'id': self.id,
                'name': self.name,
                'description': self.type,
                'category': '',
                'image': 'http://localhost:8000/static/default.avif',
            })

        if albums:
            for album in albums:
                entries_list.append({
                    'id': album.id,
                    'name': album.name,
                    'description': album.description,
                    'category': album.category,
                    'image': 'http://localhost:8000{}'.format(album.image.url),
                })
        return entries_list

    def generate_bedroom_photos(self):
        entries_list = []
        albums = self.bedroomphoto_set.filter(display=True)
        if albums:
            for album in albums:
                entries_list.append({
                    'id': album.id,
                    'name': album.name,
                    'description': album.description,
                    'category': 'Bedroom' if not album.bedroom.master_bedroom else 'Master Bedroom',
                    'image': 'http://localhost:8000{}'.format(album.image.url),
                })
        return entries_list

    def generate_bathroom_photos(self):
        entries_list = []
        albums = self.bathroomphoto_set.filter(display=True)
        if albums:
            for album in albums:
                entries_list.append({
                    'id': album.id,
                    'name': album.name,
                    'description': album.description,
                    'category': '{} Bathroom'.format(album.bathroom.bathroom_type),
                    'image': 'http://localhost:8000{}'.format(album.image.url),
                })
        return entries_list

    def generate_unit_album(self): 
        return self.generate_unit_photos() + self.generate_bedroom_photos() + self.generate_bathroom_photos()

    def save(self, *args, **kwargs):
        # Refresh update timestamp
        self.last_updated = timezone.now()
        # Cannot be active without at least 1 bedroom and 1 bathroom
        self.active = self.activable()
        # Send to Rabbit and let Rabbit send to Redis
        _rabbitmq_modules.add_to_rabbit_queue(
            _rabbitmq_modules.RABBIT_MQ_INSTRUCTION_CACHE_UNITS
        )
        # Save
        super().save(*args, **kwargs)


class UnitPhoto(models.Model):

    # Limit choices
    CATEGORY_CHOICES = [
        ('Living', 'Living'),
        ('Kitchen', 'Kitchen'),
        ('Balcony', 'Balcony'),
        ('Garden', 'Garden'),
    ]

    def generate_upload_path(self, instance):
        unit_name = str(self.unit.name).replace(" ", "-")
        category_name = str(self.category).replace(" ", "-")
        upload_path = "uploads/{}/{}/{}".format(
            str(unit_name).lower(), str(category_name).lower(), instance
        )
        if self.thumbnail:
            self.unit.thumbnail = upload_path
            self.unit.save()
        return upload_path

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    display = models.BooleanField(default=True)
    thumbnail = models.BooleanField(default=False)
    name = models.CharField(max_length=200, default='')
    description = models.CharField(max_length=200, default='')
    category = models.CharField(
        max_length=200,
        choices=CATEGORY_CHOICES,
        default='Living',
    )
    image = models.ImageField(upload_to=generate_upload_path, blank=True, null=True)
    created_date = models.DateTimeField("created", default=timezone.now)
    last_updated = models.DateTimeField("last updated", default=timezone.now)

    def __str__(self):
        return f"{self.name} (thumbnail: {self.thumbnail}) | {self.unit.name} | {self.category}"

    def save(self, *args, **kwargs):
        # Refresh update timestamp
        self.last_updated = timezone.now()
        # Save
        super().save(*args, **kwargs)


@receiver(post_save, sender=UnitPhoto)
def manage_units_thumbnails(sender, instance, created, **kwargs):
    if instance.thumbnail:
        if instance.unit:
            # Update Unit
            instance.unit.thumbnail = str(instance.image.url).replace('media/', '')
            instance.unit.save()
            # Disable other thumbnails
            batch = UnitPhoto.objects.filter(
                unit=instance.unit
                ).exclude(
                    id=instance.id
                    ).update(
                        thumbnail=False
                        )


class Bedroom(models.Model):

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    master_bedroom = models.BooleanField(default=False)
    bed_type = models.CharField(max_length=200, default='')
    number_of_beds = models.IntegerField(
        validators=[
            MinValueValidator(1)
        ],
        default=1
    )
    created_date = models.DateTimeField("created", default=timezone.now)
    last_updated = models.DateTimeField("last updated", default=timezone.now)

    def __str__(self):
        return f"{self.unit.name} -> room {self.id} (master: {self.master_bedroom})"

    def save(self, *args, **kwargs):
        # Refresh update timestamp
        self.last_updated = timezone.now()
        # Save
        super().save(*args, **kwargs)


@receiver(post_save, sender=Bedroom)
def manage_master_bedrooms(sender, instance, created, **kwargs):
    if instance.master_bedroom:
        if instance.unit:
            # Disable other masters
            batch = Bedroom.objects.filter(
                unit=instance.unit
                ).exclude(
                    id=instance.id
                    ).update(
                        master_bedroom=False
                        )


class BedroomPhoto(models.Model):

    def generate_upload_path(self, instance):
        unit_name = str(self.unit.name).replace(" ", "-")
        room = "room-{}".format(
            str(self.bedroom.id).replace(" ", "-")
        )
        upload_path = "uploads/{}/rooms/{}/{}".format(
            str(unit_name).lower(), str(room).lower(), instance
        )
        return upload_path

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    bedroom = models.ForeignKey(Bedroom, on_delete=models.CASCADE)
    display = models.BooleanField(default=True)
    name = models.CharField(max_length=200, default='')
    description = models.CharField(max_length=200, default='')
    image = models.ImageField(upload_to=generate_upload_path)
    created_date = models.DateTimeField("created", default=timezone.now)
    last_updated = models.DateTimeField("last updated", default=timezone.now)

    def __str__(self):
        return f"{self.name} | {self.unit.name} -> room {self.bedroom.id} (master: {self.bedroom.master_bedroom})"

    def save(self, *args, **kwargs):
        # Refresh update timestamp
        self.last_updated = timezone.now()
        # Save
        super().save(*args, **kwargs)


class Bathroom(models.Model):

    # Limit choices
    UNIT_TYPE_CHOICES = [
        ('Full', 'Full'),
        ('Half', 'Half'),
    ]

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    bathroom_type = models.CharField(
        max_length=200,
        choices=UNIT_TYPE_CHOICES,
        default='Full',
    )
    created_date = models.DateTimeField("created", default=timezone.now)
    last_updated = models.DateTimeField("last updated", default=timezone.now)

    def __str__(self):
        return f"{self.unit.name} -> bathroom {self.id} (type: {self.bathroom_type})"

    def save(self, *args, **kwargs):
        # Refresh update timestamp
        self.last_updated = timezone.now()
        # Save
        super().save(*args, **kwargs)


class BathroomPhoto(models.Model):

    def generate_upload_path(self, instance):
        unit_name = str(self.unit.name).replace(" ", "-")
        bathroom = "bathroom-{}".format(
            str(self.bathroom.id).replace(" ", "-")
        )
        upload_path = "uploads/{}/bathrooms/{}/{}".format(
            str(unit_name).lower(), str(bathroom).lower(), instance
        )
        return upload_path

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    bathroom = models.ForeignKey(Bathroom, on_delete=models.CASCADE)
    display = models.BooleanField(default=True)
    name = models.CharField(max_length=200, default='')
    description = models.CharField(max_length=200, default='')
    image = models.ImageField(upload_to=generate_upload_path)
    created_date = models.DateTimeField("created", default=timezone.now)
    last_updated = models.DateTimeField("last updated", default=timezone.now)

    def __str__(self):
        return f"{self.name} | {self.unit.name} -> bathroom {self.bathroom.id} (type {self.bathroom.bathroom_type})"

    def save(self, *args, **kwargs):
        # Refresh update timestamp
        self.last_updated = timezone.now()
        # Save
        super().save(*args, **kwargs)


class Booking(models.Model):

    def default_check_out():
        return datetime.date.today() + datetime.timedelta(days=1)

    def default_time():
        return datetime.datetime.now().time()

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    check_in = models.DateField(default=datetime.date.today)
    check_in_time = models.TimeField(default=default_time)
    check_out = models.DateField(default=default_check_out)
    check_out_time = models.TimeField(default=default_time)
    guest_email = models.EmailField(max_length=254, default='')
    guest_origin = models.CharField(max_length=200, default='')
    guests_number = models.IntegerField(
        validators=[
            MinValueValidator(1)
        ],
        default=1
    )
    breakfast = models.BooleanField(default=True)
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    card_number = models.CharField(max_length=200, default='')
    card_expiry = models.CharField(max_length=200, default='')
    card_cvc = models.CharField(max_length=200, default='')
    card_name = models.CharField(max_length=200, default='')
    created_date = models.DateTimeField("created", default=timezone.now)
    last_updated = models.DateTimeField("last updated", default=timezone.now)

    def __str__(self):
        return f"{self.check_in} -> {self.check_out} | {self.unit.name} | {self.duration_calculator()} night(s) | Made on {self.created_date}"

    def duration_calculator(self):
        return int((self.check_out - self.check_in).days)

    def generate_calendar(self):
        duration = self.duration_calculator()
        calendar = []
        for i in range(duration + 1):
            calendar.append(
                self.check_in + datetime.timedelta(days=i)
            )
        return calendar

    def save(self, *args, **kwargs):
        # Refresh update timestamp
        self.last_updated = timezone.now()
        # Save
        super().save(*args, **kwargs)

    # On Save, cache to Redis and event on Kafka

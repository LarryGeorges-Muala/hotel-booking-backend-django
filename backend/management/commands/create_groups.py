from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from backend import models


def generate_permissions(permission_level, model_field, model_content_type):
    if str(permission_level).lower() == 'admin':
        return Permission.objects.filter(
                codename__in=[
                    'add_{}'.format(
                        str(model_field).lower()
                    ),
                    'change_{}'.format(
                        str(model_field).lower()
                    ),
                    'delete_{}'.format(
                        str(model_field).lower()
                    ),
                    'view_{}'.format(
                        str(model_field).lower()
                    ),
                ],
                content_type=model_content_type,
            )
    if str(permission_level).lower() == 'editor':
        return Permission.objects.filter(
                codename__in=[
                    'add_{}'.format(
                        str(model_field).lower()
                    ),
                    'change_{}'.format(
                        str(model_field).lower()
                    ),
                    'view_{}'.format(
                        str(model_field).lower()
                    ),
                ],
                content_type=model_content_type,
            )
    return Permission.objects.filter(
            codename__in=[
                'view_{}'.format(
                    str(model_field).lower()
                ),
            ],
            content_type=model_content_type,
        )


class Command(BaseCommand):
    help = "Bootstrap Groups"

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            nargs='?',
            type=str,
            default=''
        )

        parser.add_argument(
            '--password',
            nargs='?',
            type=str,
            default=''
        )

        parser.add_argument(
            '--permission_level',
            nargs='?',
            type=str,
            default='viewer'
        )

    def handle(self, *args, **options):
        username = options.get("username", "")
        password = options.get("password", "")
        permission_level = options.get("permission_level", "viewer")

        self.stdout.write(
            self.style.WARNING(f"BOOTSTRAPPING GROUPS...")
        )
        try:
            # Groups
            developer_admins_group, created = Group.objects.get_or_create(name='Admins')
            developer_editors_group, created = Group.objects.get_or_create(name='Editors')
            developer_viewers_group, created = Group.objects.get_or_create(name='Viewers')

            # Models
            user_content_type = ContentType.objects.get_for_model(models.User)
            client_content_type = ContentType.objects.get_for_model(models.Client)
            unit_content_type = ContentType.objects.get_for_model(models.Unit)
            unit_photo_content_type = ContentType.objects.get_for_model(models.UnitPhoto)
            bedroom_content_type = ContentType.objects.get_for_model(models.Bedroom)
            bedroom_photo_content_type = ContentType.objects.get_for_model(models.BedroomPhoto)
            bathroom_content_type = ContentType.objects.get_for_model(models.Bathroom)
            bathroom_photo_content_type = ContentType.objects.get_for_model(models.BathroomPhoto)
            booking_content_type = ContentType.objects.get_for_model(models.Booking)

            # Permissions - users
            users_admins_permissions = generate_permissions(
                'admin',
                'user',
                user_content_type
            )
            users_editors_permissions = generate_permissions(
                'editor',
                'user',
                user_content_type
            )
            users_viewers_permissions = generate_permissions(
                'viewer',
                'user',
                user_content_type
            )

            # Permissions - clients
            clients_admins_permissions = generate_permissions(
                'admin',
                'client',
                client_content_type
            )
            clients_editors_permissions = generate_permissions(
                'editor',
                'client',
                client_content_type
            )
            clients_viewers_permissions = generate_permissions(
                'viewer',
                'client',
                client_content_type
            )

            # Permissions - units
            units_admins_permissions = generate_permissions(
                'admin',
                'unit',
                unit_content_type
            )
            units_editors_permissions = generate_permissions(
                'editor',
                'unit',
                unit_content_type
            )
            units_viewers_permissions = generate_permissions(
                'viewer',
                'unit',
                unit_content_type
            )

            # Permissions - unit photos
            unit_photos_admins_permissions = generate_permissions(
                'admin',
                'unitphoto',
                unit_photo_content_type
            )
            unit_photos_editors_permissions = generate_permissions(
                'editor',
                'unitphoto',
                unit_photo_content_type
            )
            unit_photos_viewers_permissions = generate_permissions(
                'viewer',
                'unitphoto',
                unit_photo_content_type
            )

            # Permissions - bedrooms
            bedrooms_admins_permissions = generate_permissions(
                'admin',
                'bedroom',
                bedroom_content_type
            )
            bedrooms_editors_permissions = generate_permissions(
                'editor',
                'bedroom',
                bedroom_content_type
            )
            bedrooms_viewers_permissions = generate_permissions(
                'viewer',
                'bedroom',
                bedroom_content_type
            )

            # Permissions - bedroom photos
            bedroom_photos_admins_permissions = generate_permissions(
                'admin',
                'bedroomphoto',
                bedroom_photo_content_type
            )
            bedroom_photos_editors_permissions = generate_permissions(
                'editor',
                'bedroomphoto',
                bedroom_photo_content_type
            )
            bedroom_photos_viewers_permissions = generate_permissions(
                'viewer',
                'bedroomphoto',
                bedroom_photo_content_type
            )

            # Permissions - bathrooms
            bathrooms_admins_permissions = generate_permissions(
                'admin',
                'bathroom',
                bathroom_content_type
            )
            bathrooms_editors_permissions = generate_permissions(
                'editor',
                'bathroom',
                bathroom_content_type
            )
            bathrooms_viewers_permissions = generate_permissions(
                'viewer',
                'bathroom',
                bathroom_content_type
            )

            # Permissions - bathroom photos
            bathroom_photos_admins_permissions = generate_permissions(
                'admin',
                'bathroomphoto',
                bathroom_photo_content_type
            )
            bathroom_photos_editors_permissions = generate_permissions(
                'editor',
                'bathroomphoto',
                bathroom_photo_content_type
            )
            bathroom_photos_viewers_permissions = generate_permissions(
                'viewer',
                'bathroomphoto',
                bathroom_photo_content_type
            )

            # Permissions - bookings
            bookings_admins_permissions = generate_permissions(
                'admin',
                'booking',
                booking_content_type
            )
            bookings_editors_permissions = generate_permissions(
                'editor',
                'booking',
                booking_content_type
            )
            bookings_viewers_permissions = generate_permissions(
                'viewer',
                'booking',
                booking_content_type
            )

            # Permissions assignment - admins
            developer_admins_group.permissions.add(*users_admins_permissions)
            developer_admins_group.permissions.add(*clients_admins_permissions)
            developer_admins_group.permissions.add(*units_admins_permissions)
            developer_admins_group.permissions.add(*unit_photos_admins_permissions)
            developer_admins_group.permissions.add(*bedrooms_admins_permissions)
            developer_admins_group.permissions.add(*bedroom_photos_admins_permissions)
            developer_admins_group.permissions.add(*bathrooms_admins_permissions)
            developer_admins_group.permissions.add(*bathroom_photos_admins_permissions)
            developer_admins_group.permissions.add(*bookings_admins_permissions)

            # Permissions assignment - editors
            developer_editors_group.permissions.add(*users_editors_permissions)
            developer_editors_group.permissions.add(*clients_editors_permissions)
            developer_editors_group.permissions.add(*units_editors_permissions)
            developer_editors_group.permissions.add(*unit_photos_editors_permissions)
            developer_editors_group.permissions.add(*bedrooms_editors_permissions)
            developer_editors_group.permissions.add(*bedroom_photos_editors_permissions)
            developer_editors_group.permissions.add(*bathrooms_editors_permissions)
            developer_editors_group.permissions.add(*bathroom_photos_editors_permissions)
            developer_editors_group.permissions.add(*bookings_editors_permissions)

            # Permissions assignment - viewers
            developer_viewers_group.permissions.add(*clients_viewers_permissions)
            developer_viewers_group.permissions.add(*units_viewers_permissions)
            developer_viewers_group.permissions.add(*unit_photos_viewers_permissions)
            developer_viewers_group.permissions.add(*bedrooms_viewers_permissions)
            developer_viewers_group.permissions.add(*bedroom_photos_viewers_permissions)
            developer_viewers_group.permissions.add(*bathrooms_viewers_permissions)
            developer_viewers_group.permissions.add(*bathroom_photos_viewers_permissions)
            developer_viewers_group.permissions.add(*bookings_viewers_permissions)

        except Exception as e:
            raise CommandError(e)

        if username:
            self.stdout.write(
                self.style.WARNING('BOOTSTRAPPING USER `{}` :'.format(username))
            )
            self.stdout.write(
                self.style.WARNING('PERMISSION LEVEL: `{}`'.format(permission_level))
            )
            try:
                user, created = User.objects.get_or_create(
                    username=username
                )
                user.is_staff = True
                user.save()

                if password:
                    user.set_password(password)
                    user.save()

                match permission_level:
                    case 'superuser':
                        self.stdout.write(
                            self.style.WARNING(
                                'SETTING PERMISSION LEVEL SUPERUSER'
                            )
                        )
                        user.is_superuser = True
                        user.save()
                    case 'admin':
                        self.stdout.write(
                            self.style.WARNING(
                                'SETTING PERMISSION LEVEL: `{}`'.format(
                                    permission_level
                                )
                            )
                        )
                        user.groups.add(developer_admins_group)
                    case 'editor':
                        self.stdout.write(
                            self.style.WARNING(
                                'SETTING PERMISSION LEVEL: `{}`'.format(
                                    permission_level
                                )
                            )
                        )
                        user.groups.add(developer_editors_group)
                    case _:
                        self.stdout.write(
                            self.style.WARNING(
                                'SETTING PERMISSION LEVEL: `{}`'.format(
                                    permission_level
                                )
                            )
                        )
                        user.groups.add(developer_viewers_group)

            except Exception as e:
                raise CommandError(e)


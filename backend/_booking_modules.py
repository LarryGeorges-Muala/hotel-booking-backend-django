import json, re, pycountry, ast
from django.conf import settings
from datetime import date, datetime, timedelta
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet
from . import models
from common import _common_modules, _rabbitmq_modules, _redis_modules


'''
    Units - Load Details
'''
def load_and_cache_units_details(cached_units_key=_common_modules.CACHED_UNITS_KEY_GLOBAL):
    units_list = []
    try:
        units = models.Unit.objects.filter(
            active=True
        )
        for unit in units:
            # Load calendar per unit
            calendar = []
            booking_entries = unit.booking_set.all()
            for entry in booking_entries:
                calendar = calendar + entry.generate_calendar()
            calendar = list(dict.fromkeys(calendar))

            # Find a gap in the calendar
            next_available = date.today()
            for i in range(365):
                check = date.today() + timedelta(days=i)
                next_available = check
                if check not in calendar:
                    break

            # Load details per active unit
            if unit.active:
                units_list.append({
                    'id': unit.id,
                    'thumbnail': 'http://localhost:8000/media/{}'.format(unit.thumbnail) if unit.thumbnail else 'http://localhost:8000/media/demo/thumbnail/thumbnail.png',
                    'name': unit.name,
                    'type': unit.type,
                    'number_of_rooms': unit.number_of_rooms_in_unit(),
                    'number_of_bathrooms': unit.number_of_bathrooms_in_unit(),
                    'price': unit.price,
                    'occupancy': unit.occupancy,
                    'breakfast': unit.breakfast,
                    'breakfast_price': unit.breakfast_price,
                    'calendar': calendar,
                    'next_available': next_available,
                    'album': unit.generate_unit_album(),
                })

        # Cache Units
        _redis_modules.create_redis_session(
            cached_units_key,
            {
                'untis_list': json.dumps(units_list, default=str)
            },
            False
        )
    except Exception as e:
        _common_modules.logger_error(e)
    return units_list


'''
Units - Query Cache or DB
'''
def load_units_from_cache_or_database(payload):
    try:
        units_list = []
        cached_units_key = _common_modules.CACHED_UNITS_KEY_GLOBAL

        ''' From Redis '''
        cached_units = _redis_modules.fetch_redis_session(cached_units_key)
        if cached_units:
            units_list = cached_units.get('untis_list', [])
            if type(units_list) == str:
                units_list = json.loads(units_list)

        ''' From DB '''
        if not cached_units or not units_list:
            if not isinstance(payload, dict):
                payload = json.loads(payload)
            units_list = load_and_cache_units_details(cached_units_key)
        
        ''' Add units to payload '''
        payload['units'] = units_list
    except Exception as e:
        _common_modules.logger_error(e)
    return payload


'''
Test Each Booking Field
'''
def test_booking_fields(booking_data, booking_field):
    try:
        _common_modules.logger_info(f"Checking field '{booking_field}'...")
        if booking_field in booking_data:
            _common_modules.logger_info(f"'{booking_field}' valid..")
            return True
        else:
            _common_modules.logger_info(f"'{booking_field}' missing..")
    except Exception as e:
        _common_modules.logger_error(e)
    return False


'''
Validate Email
'''
def is_email_valid(email):
    try:
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.fullmatch(regex, email):
            return True
    except Exception as e:
        _common_modules.logger_error(e)
    return False


'''
Validate Origin Country
'''
def is_country_valid(country):
    try:
        check = pycountry.countries.get(alpha_2=country)
        if check:
            _common_modules.logger_info(f"'{country}' valid..")
            return True
        else:
            _common_modules.logger_info(f"'{country}' invalid..")
    except Exception as e:
        _common_modules.logger_error(e)
    return False


'''
Main Guest Important Fields Validation
'''
def main_guest_validator(booking_data, booking_field):
    try:
        match booking_field:
            case 'email':
                is_email_valid(booking_data['email'])
            case 'phone':
                _common_modules.logger_info('No validation required - Phone number optional...')
            case 'countriesfield':
                is_country_valid(booking_data['countriesfield'])
            case _:
                _common_modules.logger_info('No validation required...')
        return True
    except Exception as e:
        _common_modules.logger_error(e)
    return False


'''
Confirm Booking Main Guest
'''
def confirm_booking_main_guest(booking_data, booking_field):
    try:
        _common_modules.logger_info(f'''Checking field '{booking_field}'...''')

        # Filtering main guest
        if 'main_guest' in str(booking_field).lower():
            if 'main_guest' in booking_data:
                _common_modules.logger_info(f'''{booking_field} - Main guest loaded...''')
                main_guest_dict = json.loads(booking_field)
                main_guest = main_guest_dict['main_guest']
                for key, value in main_guest.items():
                    test_booking_fields(main_guest, key)
                    main_guest_validator(main_guest, key)
                return True
            else:
                _common_modules.logger_error(f'''{booking_field} - Main guest missing...''')
        else:
            _common_modules.logger_error(f'''Main guest details missing from field \n '{booking_field}'... ''')
    except Exception as e:
        _common_modules.logger_error(e)
    return False


'''
Valdate Booking Fields
'''
def validate_booking_fields(booking_data):
    try:
        # Hardcoded fields to validate - Main Guest
        booking_main_guest = [
            '{"main_guest": ["title", "firstname", "surname", "email", "phone", "countriesfield"]}'
        ]
        # Hardcoded fields to validate - Booking Details
        booking_fields = [
            'guests_number',
            'breakfast',
            'check_in',
            'check_out',
            'check_in_time',
            'check_out_time',
        ]

        # Validation Main Guest
        confirm_booking_main_guest(booking_data, booking_main_guest[0])
        _common_modules.improve_log_readability()

        # Validation Details Loop
        for field in booking_fields:
            test_booking_fields(booking_data, field)
        return True
    except Exception as e:
        _common_modules.logger_error(e)
    return False


'''
Generate Earliest Validation Date
'''
def earliest_date():
    now = datetime.now()
    today = datetime(now.year, now.month, now.day)
    return today


'''
Validate Date Format
'''
def validate_booking_dates_format(date_entry, date_entry_name):
    try:
        if '-' in str(date_entry).lower(): 
            if ' ' not in str(date_entry).lower():
                _common_modules.logger_info(f''''{date_entry_name}' - '{date_entry}' valid... ''')
                return True
            else:
                _common_modules.logger_error(f'''Invalid date format from '{date_entry_name}' - '{date_entry}' - Please use format 'YYYY-MM-DD'...''')
        else:
            _common_modules.logger_error(f'''Invalid date format from '{date_entry_name}' - '{date_entry}' - Please use format 'YYYY-MM-DD'...''')
    except Exception as e:
        _common_modules.logger_error(e)
    return False


'''
Read Booking Dates
'''
def read_booking_dates(date_entry, date_entry_name):
    try:
        if (date_entry):
            if validate_booking_dates_format(date_entry, date_entry_name):
                date_obj = datetime.strptime(
                    (date_entry.split('T'))[0],
                    "%Y-%m-%d"
                )
                today = earliest_date()
                if today <= date_obj:
                    return date_obj
                else:
                    _common_modules.logger_error(f'''Invalid date format from '{date_entry_name}' - '{date_entry}' - Please set a recent date...''')
            else:
                _common_modules.logger_error(f'''Invalid date format from '{date_entry_name}' - '{date_entry}'...''')
        else:
            _common_modules.logger_error(f'''Invalid date format from '{date_entry_name}' - '{date_entry}'...''')
    except Exception as e:
        _common_modules.logger_error(e)
    return None


'''
Calculate Booking Duration
'''
def calculate_booking_duration(checkin, checkout):
    try:
        return (datetime(checkout.year, checkout.month, checkout.day) - datetime(checkin.year, checkin.month, checkin.day)).days
    except Exception as e:
        _common_modules.logger_error(e)
    return 0


'''
Compare Booking Dates
'''
def compare_booking_dates(checkin, checkout):
    try:
        if checkin < checkout:
            # if int(checkin.timestamp() * 1000) < int(checkout.timestamp() * 1000):
            if mark_time(checkin) < mark_time(checkout):
                days_difference = calculate_booking_duration(checkin, checkout)
                _common_modules.logger_info(f''' Duration: {days_difference} night(s)''')
                return days_difference
            else:
                _common_modules.logger_error(f'''Invalid Check-Out Date from '{checkout}' compared to '{checkin}'...''')
        else:
            _common_modules.logger_error(f'''Invalid Check-Out Date from '{checkout}' compared to '{checkin}'...''')
    except Exception as e:
        _common_modules.logger_error(e)
    return 0


'''
Generate Booking Times
'''
def generate_booking_times(date_entry, time_entry, description):
    try:
        time_list = str(time_entry).split(':')
        genarated_date = datetime(
            date_entry.year,
            date_entry.month,
            date_entry.day,
            int(time_list[0]),
            int(time_list[1])
        )
        _common_modules.logger_info(f''' '{description} time': '{time_entry}' / {genarated_date}... ''')
        return genarated_date
    except Exception as e:
        _common_modules.logger_error(e)
    return None


'''
Room Availability
'''
def normalize_date(date_entry):
    return date_entry.strftime("%Y-%m-%d")

def check_room_availability(checkin, checkout, booking_duration):
    try:
        return [
            checkin,
            checkout,
            {
                'stateChanged': False,
                'stateChangedSummary': ''
            }
        ]
    except Exception as e:
        _common_modules.logger_error(e)
    return []


'''
Guests Pricing
'''
def guest_price_value():
    return 100
def breakfast_price_value():
    return 30

def generate_guests_price(booking_duration, guests_number, breakfast, unit_id):
    total = 0
    price_guest = 0
    breakfast_price = 0
    try:
        unit = models.Unit.objects.get(pk=unit_id)
        if unit:
            price_guest = unit.price
            breakfast_price = unit.breakfast_price
        breakfast_enabled = str(breakfast)
        breakfast_enabled = breakfast_enabled in ['true', 'on']
        _common_modules.logger_info(f''' USD {price_guest:,} per guest per night... ''')

        if breakfast_enabled:
            total = int(booking_duration) * int(guests_number) * (price_guest + breakfast_price)
            _common_modules.logger_info(f'''
    Including breakfast...
    USD {breakfast_price:,} per guest per breakfast...
    For {guests_number} guest(s) with breakfast and {booking_duration} night(s): USD {total:,}...
            ''')
        else:
            total = int(booking_duration) * int(guests_number) * price_guest
            _common_modules.logger_info(f'''
    For {guests_number} guest(s) and {booking_duration} night(s): USD {total:,}...
            ''')
    except Exception as e:
        _common_modules.logger_error(e)
    return total


'''
Format Content
'''
def capitalize_first_letter(text):
    try:
        if not text:
            return text
        return text[:1].upper() + text[1:]
    except Exception as e:
        _common_modules.logger_error(e)
    return ''

def interpret_option(handler):
    try:
        handler = (str(handler).lower() in ['true', 'on'])
        if handler:
            return capitalize_first_letter('yes')
        else:
            return capitalize_first_letter('no')
    except Exception as e:
        _common_modules.logger_error(e)
    return ''

def render_option_summary(handler, unit_id):
    try:
        price_guest = 0
        breakfast_price = 0
        unit = models.Unit.objects.get(pk=unit_id)
        if unit:
            price_guest = unit.price
            breakfast_price = unit.breakfast_price
        handler = (str(handler).lower() in ['true', 'on'])
        if handler:
            return f'''
    With breakfast included

    Notes:
    USD {price_guest:,} per guest per night
    USD {breakfast_price:,} per guest per breakfast

    Enjoy Your Stay!
            '''
        return f'''
    Notes:
    USD {price_guest:,} per guest per night

    Enjoy Your Stay!
    '''
    except Exception as e:
        _common_modules.logger_error(e)
    return ''

def mark_time(date_entry):
    try:
        return int(date_entry.timestamp() * 1000)
    except Exception as e:
        _common_modules.logger_error(e)
    return None


'''
Handle Booking
'''
def create_booking(payload, payload_type):
    booking_finalization = {}
    try:
        payload = _common_modules.format_request_parameters(payload, payload_type)

        booking_id = mark_time(datetime.now())
        registration_id = datetime.now()

        _common_modules.improve_log_readability()
        validate_booking_fields(payload)
        _common_modules.improve_log_readability()

        booking_checkin = read_booking_dates(
            payload['check_in'],
            'check-in'
        )
        _common_modules.improve_log_readability()
        booking_checkout = read_booking_dates(
            payload['check_out'],
            'check-out'
        )

        _common_modules.improve_log_readability()
        booking_duration = compare_booking_dates(
            booking_checkin,
            booking_checkout
        )

        _common_modules.improve_log_readability()
        booking_stay_confirmation = check_room_availability(
            booking_checkin,
            booking_checkout,
            booking_duration
        )
        booking_state = booking_stay_confirmation[2]

        _common_modules.improve_log_readability()
        booking_checkin_time = generate_booking_times(
            booking_stay_confirmation[0],
            payload['check_in_time'],
            'check-in'
        )
        _common_modules.improve_log_readability()
        booking_checkout_time = generate_booking_times(
            booking_stay_confirmation[1],
            payload['check_out_time'],
            'check-out'
        )

        _common_modules.improve_log_readability()
        booking_price = generate_guests_price(
            booking_duration,
            payload['guests_number'],
            payload['breakfast'],
            payload['unit_id']
        )

        _common_modules.improve_log_readability()
        main_guest = f"{capitalize_first_letter(payload['title'])} {capitalize_first_letter(payload['firstname'])} {capitalize_first_letter(payload['surname'])}"

        booking_finalization = {
            'booking_id': str(booking_id),
            'registration_date': str(registration_id),
            'main_guest': str(main_guest),
            'title': payload['title'],
            'firstname': payload['firstname'],
            'surname': payload['surname'],
            'origin': capitalize_first_letter(payload['countriesfield']),
            'email': payload['email'],
            'phone': payload['phone'],
            'guests': payload['guests_number'],
            'breakfast': interpret_option(payload['breakfast']),
            'breakfast_text': render_option_summary(payload['breakfast'], payload['unit_id']),
            'check_in': str(booking_checkin_time),
            'check_in_timestamp': mark_time(booking_checkin_time),
            'check_in_form': normalize_date(booking_checkin_time),
            'check_out': str(booking_checkout_time),
            'check_out_timestamp': mark_time(booking_checkout_time),
            'check_out_form': normalize_date(booking_checkout_time),
            'duration': str(booking_duration),
            'duration_text': f'{booking_duration} Night(s)',
            'price': str(booking_price),
            'price_text': f'USD {booking_price:,}',
            'bookingState': booking_state,
            'summary': f'''
    Dear {main_guest},

    Booking #{booking_id} Confirmed 
    For
    {payload['guests_number']} guest(s)  
    For
    {booking_duration} night(s)
    From 
    {booking_checkin_time}
    To 
    {booking_checkout_time}
    At the value of
    USD {booking_price:,}
    {render_option_summary(payload['breakfast'], payload['unit_id'])}
        ''',
        }

        try:
            cipher_suite = Fernet(
                settings.CRYPTOGRAPHY_KEY
            )
            unit = models.Unit.objects.get(
                pk=payload['unit_id']
            )
            unit.booking_set.create(
                card_number = cipher_suite.encrypt(
                    str(payload.get('number', '')).encode('utf-8')
                ),
                card_expiry = cipher_suite.encrypt(
                    str(payload.get('expiry', '')).encode('utf-8')
                ),
                card_cvc = cipher_suite.encrypt(
                    str(payload.get('cvc', '')).encode('utf-8')
                ),
                card_name = cipher_suite.encrypt(
                    str(payload.get('name', '')).encode('utf-8')
                ),
                check_in = booking_checkin_time,
                check_in_time = booking_checkin_time,
                check_out = booking_checkout_time,
                check_out_time = booking_checkout_time,
                guest_email = payload['email'],
                guest_origin = capitalize_first_letter(payload['countriesfield']),
                guests_number = payload['guests_number'],
                breakfast = (payload['breakfast'] in ['true', 'on']),
                total = booking_price
            )
        except Exception as e:
            _common_modules.logger_error(e)

        if booking_state['stateChanged'] == False:
            redis_payload = booking_finalization.copy()
            redis_payload.pop('bookingState', None)
            redis_payload.pop('summary', None)
            # Sessions
            _redis_modules.create_redis_session(payload['email'], redis_payload)
            # Unique Bookings
            _redis_modules.create_redis_session(str(booking_id), redis_payload)
            # Queue
            _rabbitmq_modules.add_to_rabbit_queue(str(booking_id))
            _rabbitmq_modules.add_to_rabbit_queue(redis_payload, 'json')
    except Exception as e:
        _common_modules.logger_error(e)
    return booking_finalization


'''
Handle Client IP
'''
def handle_client_ip(payload):
    client_ip = ''
    try:
        client_ip = payload.get('accessClient', '')
        if not client_ip:
            raise ValidationError('Client IP missing')
    except Exception as e:
        _common_modules.logger_error(e)
        raise
    return client_ip        


'''
Create User Session
'''
def create_user_session(payload, payload_type):
    session_status = {
        'message': 'Creating session failed',
        'status': 'failure',
        'code': 400
    }
    try:
        payload = _common_modules.format_request_parameters(payload, payload_type)
        client_ip = handle_client_ip(payload)
        _redis_modules.create_redis_session(
            client_ip,
            payload
        )
        session_status = {
            'message': 'Session created',
            'status': 'success',
            'code': 200
        }
    except Exception as e:
        _common_modules.logger_error(e)
    return session_status


'''
Fetch User Session
'''
def fetch_user_session(payload, payload_type):
    user_session = {
        'code': 400,
        'status': 'failure',
        'message': 'User session not found'
    }
    try:
        payload = _common_modules.format_request_parameters(payload, payload_type)
        client_ip = handle_client_ip(payload)
        user_session = _redis_modules.fetch_redis_session(client_ip)
        user_session = load_units_from_cache_or_database(user_session)
    except Exception as e:
        _common_modules.logger_error(e)
    return user_session


'''
Delete User Session
'''
def delete_user_session(payload, payload_type):
    session_status = {
        'message': 'Clearing session failed',
        'status': 'failure',
        'code': 400
    }
    try:
        payload = _common_modules.format_request_parameters(payload, payload_type)
        client_ip = handle_client_ip(payload)
        session_cleared = _redis_modules.clear_redis_session(client_ip)
        if session_cleared:
            session_status = {
                'message': 'Session cleared',
                'status': 'success',
                'code': 200
            }
    except Exception as e:
        _common_modules.logger_error(e)
    return session_status


'''
Fetch Dashboard Data
'''
def fetch_dashboard_data(payload, payload_type):
    try:
        payload = _common_modules.format_request_parameters(
            payload,
            payload_type
        )
        client_ip = handle_client_ip(payload)
        client_email = payload.get('email', '')
        if not client_email:
            return {
                'code': 404,
                'status': 'failure',
                'message': 'Email missing'
            }
        dashboard = models.Booking.objects.filter(
            guest_email=client_email
        )
        dashboard_data = []
        cipher_suite = Fernet(
            settings.CRYPTOGRAPHY_KEY
        )
        for entry in dashboard:
            dashboard_data.append({
                'check_in': entry.check_in,
                'check_in_time': entry.check_in_time,
                'check_out': entry.check_out,
                'check_out_time': entry.check_out_time,
                'guest_email': entry.guest_email,
                'guest_origin': entry.guest_origin,
                'guests_number': entry.guests_number,
                'breakfast': entry.breakfast,
                'total': entry.total,
                'card_number': (
                    cipher_suite.decrypt(
                        ast.literal_eval(entry.card_number)
                    )
                ).decode("utf-8") if entry.card_number else '',
                'card_expiry': (
                    cipher_suite.decrypt(
                        ast.literal_eval(entry.card_expiry)
                    )
                ).decode("utf-8") if entry.card_expiry else '',
                'card_cvc': (
                    cipher_suite.decrypt(
                        ast.literal_eval(entry.card_cvc)
                    )
                ).decode("utf-8") if entry.card_cvc else '',
                'card_name': (
                    cipher_suite.decrypt(
                        ast.literal_eval(entry.card_name)
                    )
                ).decode("utf-8") if entry.card_name else '',
            })
        return {
            'code': 200,
            'status': 'success',
            'message': 'Data found',
            'data': dashboard_data
        }
    except Exception as e:
        _common_modules.logger_error(e)
    return {
        'code': 400,
        'status': 'failure',
        'message': 'Data not found'
    }

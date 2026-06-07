import json, re
from datetime import date, datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from . import models
from common import _common_modules, _rabbitmq_modules, _redis_modules


'''
Verify User
'''
def verify_user(payload, payload_type):
    try:
        payload = _common_modules.format_request_parameters(
            payload,
            payload_type
        )
        client_email = payload.get('email', '')
        if client_email:
            try:
                models.Client.objects.get(email=client_email)
                return {
                    'code': 200,
                    'status': 'success',
                    'message': 'User exists'
                }
            except models.Client.DoesNotExist:
                return {
                    'code': 404,
                    'status': 'failure',
                    'message': 'User doesn\'t exist'
                }
        if not client_email:
            return {
                'code': 400,
                'status': 'failure',
                'message': 'No user to verify'
            }
    except Exception as e:
        _common_modules.logger_error(e)
    return {
        'code': 400,
        'status': 'failure',
        'message': 'Error verifying user'
    }


'''
Create User
'''
def create_user(request, payload, payload_type):
    try:
        payload = _common_modules.format_request_parameters(
            payload,
            payload_type
        )

        client_email = payload.get('email', '')
        if not client_email:
            return {
                'code': 404,
                'status': 'failure',
                'message': 'Email missing'
            }

        client_firstname = payload.get('firstname', '')
        if not client_firstname:
            return {
                'code': 404,
                'status': 'failure',
                'message': 'First name missing'
            }

        client_lastname = payload.get('surname', '')
        if not client_lastname:
            return {
                'code': 404,
                'status': 'failure',
                'message': 'Last name missing'
            }

        client_password = payload.get('password', '')
        if not client_password:
            return {
                'code': 404,
                'status': 'failure',
                'message': 'Password missing'
            }

        try:
            User.objects.get(
                username=client_email
            )
            return {
                'code': 400,
                'status': 'failure',
                'message': 'User already exists'
            }
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=client_email,
                email=client_email,
                password=client_password,
                first_name=client_firstname,
                last_name=client_lastname,
            )
            client = models.Client.objects.create(
                user=user,
                ip=payload.get('accessClient', ''),
                email=client_email,
                first_name=client_firstname,
                last_name=client_lastname,
                title=payload.get('title', ''),
                phone=payload.get('phone', ''),
            )
            authenticate(
                username=client_email,
                password=client_password
            )
            return {
                'code': 200,
                'status': 'success',
                'message': 'User created',
                'data': {
                    'username': client_email,
                    'userId': user.id,
                    'clientId': client.id,
                    'accessToken': get_token(request),
                }
            }

    except Exception as e:
        _common_modules.logger_error(e)
    except IntegrityError as e:
        _common_modules.logger_error(e)
        return {
            'code': 400,
            'status': 'failure',
            'message': 'User already exists'
        }
    return {
        'code': 400,
        'status': 'failure',
        'message': 'Error creating user'
    }


'''
Fetch User
'''
def fetch_user(request, payload, payload_type):
    try:
        payload = _common_modules.format_request_parameters(
            payload,
            payload_type
        )

        client_email = payload.get('email', '')
        if not client_email:
            return {
                'code': 404,
                'status': 'failure',
                'message': 'Email missing'
            }

        client_password = payload.get('password', '')
        if not client_password:
            return {
                'code': 404,
                'status': 'failure',
                'message': 'Password missing'
            }

        try:
            user = User.objects.get(
                username=client_email,
                password=client_password,
            )
            client = models.Client.objects.get(
                user=user,
                email=client_email,
            )
            authenticate(
                username=client_email,
                password=client_password
            )
            return {
                'code': 200,
                'status': 'success',
                'message': 'User found',
                'data': {
                    'username': client_email,
                    'userId': user.id,
                    'clientId': client.id,
                    'accessToken': get_token(request),
                    'firstname': client.first_name,
                    'surname': client.last_name,
                    'email': client_email,
                    'title': client.title,
                    'phone': client.phone
                }
            }
        except User.DoesNotExist:
            return {
                'code': 404,
                'status': 'failure',
                'message': 'User not found'
            }
        except models.Client.DoesNotExist:
            return {
                'code': 404,
                'status': 'failure',
                'message': 'User not found'
            }
        except Exception as e:
            _common_modules.logger_error(e)
            raise

    except Exception as e:
        _common_modules.logger_error(e)
    return {
        'code': 400,
        'status': 'failure',
        'message': 'Error fetching user'
    }

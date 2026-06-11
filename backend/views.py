import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.db.models import F
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic, View
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from . import models

from prometheus_client import generate_latest

from . import _booking_modules, _users_modules
from common import _common_modules, _otel_modules


'''
    Decorators
'''
decorator_secured_gets = [
    require_http_methods(["GET"]),
    csrf_protect
]
decorator_secured_posts = [
    require_http_methods(["POST"]),
    csrf_protect
]
decorator_relaxed_posts = [
    require_http_methods(["POST"]),
    csrf_exempt,
    ensure_csrf_cookie
]


'''
    Endpoints
'''
@method_decorator(
    decorator_secured_gets, 
    name="dispatch"
)
class PrometheusMetrics(View):
    ''' Expose Prometheus metrics, including log counters. '''
    metrics = generate_latest()  # Generate all Prometheus metrics
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            self.metrics,
            content_type='text/plain'
        )


@method_decorator(
    decorator_secured_gets, 
    name="dispatch"
)
class Health(View):
    def get(self, request):
        _otel_modules.request_counter_health_endpoint.add(
            1,
            {
                'http.method': request.method,
                'http.route': request.path
            }
        )
        return JsonResponse(
            _common_modules.health()
        )


@method_decorator(
    decorator_secured_posts, 
    name="dispatch"
)
class CreateBooking(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            _booking_modules.create_booking(
                request.body,
                'json'
            )
        )


@method_decorator(
    decorator_secured_posts, 
    name="dispatch"
)
class CreateUserSession(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            _booking_modules.create_user_session(
                request.body,
                'json'
            )
        )


@method_decorator(
    decorator_secured_posts, 
    name="dispatch"
)
class ClearUserSession(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            _booking_modules.delete_user_session(
                request.body,
                'json'
            )
        )


@method_decorator(
    decorator_relaxed_posts, 
    name="dispatch"
)
class FetchUserSession(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            _booking_modules.fetch_user_session(
                request.body,
                'json'
            )
        )


@method_decorator(
    decorator_secured_posts, 
    name="dispatch"
)
class VerifyUser(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            _users_modules.verify_user(
                request.body,
                'json'
            )
        )


@method_decorator(
    decorator_secured_posts, 
    name="dispatch"
)
class CreateUser(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            _users_modules.create_user(
                request,
                request.body,
                'json'
            )
        )


@method_decorator(
    decorator_secured_posts, 
    name="dispatch"
)
class FetchUser(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            _users_modules.fetch_user(
                request,
                request.body,
                'json'
            )
        )


@method_decorator(
    decorator_secured_posts, 
    name="dispatch"
)
class UpdateUser(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            _users_modules.update_user(
                request,
                request.body,
                'json'
            )
        )


@method_decorator(
    decorator_secured_posts, 
    name="dispatch"
)
class FetchDashboardData(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            _booking_modules.fetch_dashboard_data(
                request.body,
                'json'
            )
        )

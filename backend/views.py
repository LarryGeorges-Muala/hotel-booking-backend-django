import json, datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.db.models import F
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic, View
from django.views.decorators import csrf, http
from django.contrib.auth import decorators
from django.forms import model_to_dict
from . import models

from prometheus_client import generate_latest

from . import _booking_modules, _users_modules
from common import _common_modules, _otel_modules


'''
    Decorators
'''
decorator_secured_gets = [
    http.require_http_methods(['GET']),
    csrf.csrf_protect,
]
decorator_protected_secured_gets = [
    http.require_http_methods(['GET']),
    csrf.csrf_protect,
    decorators.login_required,
]
decorator_secured_posts = [
    http.require_http_methods(['POST']),
    csrf.csrf_protect,
]
decorator_protected_secured_posts = [
    http.require_http_methods(['POST']),
    csrf.csrf_protect,
    decorators.login_required,
]
decorator_relaxed_posts = [
    http.require_http_methods(['POST']),
    csrf.csrf_exempt,
    csrf.ensure_csrf_cookie,
]


'''
    Endpoints
'''
@method_decorator(
    decorator_secured_gets, 
    name='dispatch'
)
class Index(View):
    def get(self, request, *args, **kwargs):
        return redirect('backend:units')


@method_decorator(
    decorator_secured_gets, 
    name='dispatch'
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
    name='dispatch'
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
    name='dispatch'
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
    name='dispatch'
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
    name='dispatch'
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
    name='dispatch'
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
    name='dispatch'
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
    name='dispatch'
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
    name='dispatch'
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
    name='dispatch'
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
    name='dispatch'
)
class FetchDashboardData(View):
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            _booking_modules.fetch_dashboard_data(
                request.body,
                'json'
            )
        )


'''
Models Templates
'''
@method_decorator(
    decorator_protected_secured_gets, 
    name='dispatch'
)
class UnitListView(generic.ListView):
    queryset = models.Unit.objects.order_by('-created_date')
    context_object_name = 'units_available'
    template_name = 'backend/unit_list.html'


@method_decorator(
    decorator_protected_secured_gets, 
    name='dispatch'
)
class UnitDetailView(generic.DetailView):
    model = models.Unit
    context_object_name = 'single_unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Main
        context['unit_data'] = model_to_dict(
            super().get_object()
        )

        # UnitPhoto Queryset
        unit_photo_list = []
        for entry in models.UnitPhoto.objects.filter(
            unit=super().get_object()
        ):
            unit_photo_list.append(
                model_to_dict(entry)
            )
        context['unit_photo_data'] = unit_photo_list

        # Bedroom Queryset
        bedroom_list = []
        for entry in models.Bedroom.objects.filter(
            unit=super().get_object()
        ):
            bedroom_list.append(
                model_to_dict(entry)
            )
        context['bedroom_data'] = bedroom_list

        # BedroomPhoto Queryset
        bedroom_photo_list = []
        for entry in models.BedroomPhoto.objects.filter(
            unit=super().get_object()
        ):
            bedroom_photo_list.append(
                model_to_dict(entry)
            )
        context['bedroom_photo_data'] = bedroom_photo_list

        # Bathroom Queryset
        bathroom_list = []
        for entry in models.Bathroom.objects.filter(
            unit=super().get_object()
        ):
            bathroom_list.append(
                model_to_dict(entry)
            )
        context['bathroom_data'] = bathroom_list

        # BathroomPhoto Queryset
        bathroom_photo_list = []
        for entry in models.BathroomPhoto.objects.filter(
            unit=super().get_object()
        ):
            bathroom_photo_list.append(
                model_to_dict(entry)
            )
        context['bathroom_photo_data'] = bathroom_photo_list

        # Bookings Queryset
        bookings = models.Booking.objects.filter(
            unit=super().get_object()
        )

        bookings_list = []
        for entry in bookings.order_by('-created_date'):
            bookings_list.append(
                model_to_dict(entry)
            )
        context['bookings_data'] = bookings_list
        context['bookings_count'] = bookings.count()
        context['bookings_active'] = bookings.filter(check_out__gte=datetime.date.today()).count()
        context['bookings_completed'] = bookings.filter(check_out__lt=datetime.date.today()).count()
        return context

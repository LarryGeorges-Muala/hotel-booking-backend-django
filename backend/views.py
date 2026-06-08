import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.db.models import F
from django.urls import reverse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from prometheus_client import generate_latest

from . import _booking_modules, _users_modules
from common import _common_modules

from opentelemetry import metrics
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)


trace.set_tracer_provider(TracerProvider())

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

meter = metrics.get_meter(__name__)


def metrics_view(request):
    """Expose Prometheus metrics, including log counters."""
    metrics = generate_latest()  # Generate all Prometheus metrics
    return HttpResponse(metrics, content_type='text/plain')


@require_http_methods(['GET'])
def health(request):
    request_counter = meter.create_counter(
        name='django_health_requests_total',
        description='Total HTTP requests',
    )
    request_counter.add(1, {'http.method': request.method, 'http.route': request.path})
    return JsonResponse(
        _common_modules.health()
    )


@require_http_methods(['POST'])
@csrf_protect
def index(request):
    return JsonResponse(
        _booking_modules.create_booking(
            request.body,
            'json'
        )
    )


@require_http_methods(['POST'])
@csrf_protect
def create_user_session(request):
    return JsonResponse(
        _booking_modules.create_user_session(
            request.body,
            'json'
        )
    )


@require_http_methods(['POST'])
@csrf_protect
def clear_user_session(request):
    return JsonResponse(
        _booking_modules.delete_user_session(
            request.body,
            'json'
        )
    )


@require_http_methods(['POST'])
@csrf_exempt
@ensure_csrf_cookie
def fetch_user_session(request):
    return JsonResponse(
        _booking_modules.fetch_user_session(
            request.body,
            'json'
        )
    )


@require_http_methods(['POST'])
@csrf_protect
def verify_user(request):
    return JsonResponse(
        _users_modules.verify_user(
            request.body,
            'json'
        )
    )


@require_http_methods(['POST'])
@csrf_protect
def create_user(request):
    return JsonResponse(
        _users_modules.create_user(
            request,
            request.body,
            'json'
        )
    )


@require_http_methods(['POST'])
@csrf_protect
def fetch_user(request):
    return JsonResponse(
        _users_modules.fetch_user(
            request,
            request.body,
            'json'
        )
    )


@require_http_methods(['POST'])
@csrf_protect
def update_user(request):
    return JsonResponse(
        _users_modules.update_user(
            request,
            request.body,
            'json'
        )
    )


@require_http_methods(['POST'])
@csrf_protect
def fetch_dashboard_data(request):
    return JsonResponse(
        _booking_modules.fetch_dashboard_data(
            request.body,
            'json'
        )
    )

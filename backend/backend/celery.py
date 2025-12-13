"""
Celery Configuration for Owls E-commerce Platform
=================================================
Asynchronous task queue setup with Redis broker.
"""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('owls')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Task routing configuration
app.conf.task_routes = {
    # Email tasks go to email queue
    'users.send_password_reset_email': {'queue': 'email'},
    'users.send_welcome_email': {'queue': 'email'},
    'users.send_verification_email': {'queue': 'email'},
    
    # Maintenance tasks go to maintenance queue
    'users.cleanup_expired_sessions': {'queue': 'maintenance'},
    'users.cleanup_unverified_users': {'queue': 'maintenance'},
    'cart.cleanup_expired_carts': {'queue': 'maintenance'},
    
    # Cart tasks go to default queue
    'cart.send_abandoned_cart_reminder': {'queue': 'email'},
    'cart.identify_abandoned_carts': {'queue': 'default'},
}

# Task priority configuration
app.conf.task_default_priority = 5
app.conf.task_queue_max_priority = 10

# Result backend settings
app.conf.result_expires = 3600  # Results expire after 1 hour

# Task execution settings
app.conf.task_acks_late = True  # Tasks acknowledged after completion
app.conf.task_reject_on_worker_lost = True  # Requeue if worker dies
app.conf.worker_prefetch_multiplier = 1  # One task at a time per worker


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')


# Health check task
@app.task(name='celery.ping')
def ping():
    """Health check task to verify Celery is running."""
    return 'pong'

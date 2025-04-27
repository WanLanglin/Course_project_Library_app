from django import template
from ..models import AccessRequest

register = template.Library()

@register.filter
def has_pending_request(collection, user):
    return AccessRequest.objects.filter(
        collection=collection,
        user=user,
        status='pending'
    ).exists()

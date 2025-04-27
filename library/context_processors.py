from .models import Notification

def librarian_status(request):
    """
    Add librarian status to context for all templates.
    """
    if request.user.is_authenticated:
        return {'is_librarian': request.user.groups.filter(name="Librarian").exists()}
    return {'is_librarian': False}

def unread_notifications(request):
    """
    Add the unread notifications count to all templates.
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_count': unread_count}
    return {'unread_count': 0}

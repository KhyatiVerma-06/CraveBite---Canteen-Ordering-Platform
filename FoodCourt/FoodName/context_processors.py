from .models import OrderNotification


def notification_count(request):

    if request.user.is_authenticated:
        unread_count = OrderNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
    else:
        unread_count = 0

    return {
        'unread_notification_count': unread_count
    }
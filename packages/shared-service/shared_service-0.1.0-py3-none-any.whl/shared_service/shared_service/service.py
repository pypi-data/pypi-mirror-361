from django.conf import settings
from .models import ServiceLog

class CoreService:

    @classmethod
    def log_action(cls, user=None, action="", status="success"):
        log_entry = ServiceLog.objects.create(
            user=user,
            action=action,
            status=status
        )
        return log_entry
    
    @classmethod
    def send_notification(cls, user, message):
        cls.log_action(
            user = user,
            action="send_notification",
            status="success"
        )
        return True
    
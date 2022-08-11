from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class Rider(models.Model):
    user = models.OneToOneField("delivery.User", on_delete=models.CASCADE)

    def __str__(self):
        return f'{str(self.user)} (Rider)'
    
    @property
    def current_session(self):
        try:
            return Session.objects.get(rider=self, start_datetime__lte=timezone.now(),
                                       end_datetime__gt=timezone.now())
        except Session.DoesNotExist:
            return None

class Session(models.Model):
    rider = models.ForeignKey("Rider", on_delete=models.CASCADE)
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField()

    def __str__(self):
        return f'Session by {str(self.rider)}: {str(self.start_datetime)} - {str(self.end_datetime)}' 


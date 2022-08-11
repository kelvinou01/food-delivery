
from rest_framework.exceptions import ValidationError

from rider.models import Session


class ActiveSessionMixin:
    '''
    Checks if the session specified in the url kwarg is the user's active session.
    Call self.check_session_is_active() somewhere in your view to use this mixin.
    '''
    def check_session_is_active(self):
        session_from_kwarg = Session.objects.get(id=self.kwargs['session_id'])
        if session_from_kwarg != self.request.user.rider.current_session:
            raise ValidationError('Session is not active')



from functools import cache


class CurrentSessionMixin:
    '''
    Provides the `get_current_session` method
    '''

    @cache
    def get_current_session(self):
        return self.request.user.rider.current_session



class CurrentSessionMixin:
    '''
    Provides the `get_current_session` method
    '''

    def get_current_session(self):
        return self.request.user.rider.current_session

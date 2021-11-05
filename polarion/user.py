from .factory import Creator


class User(object):
    """
    A polarion user

    :param polarion: Polarion client object
    :param polarion_record: The user record

    """

    def __init__(self, polarion, polarion_record=None, uri=None):
        self._polarion = polarion
        self._polarion_record = polarion_record
        self._uri = uri

        if uri is not None:
            service = self._polarion.getService('Project')
            self._polarion_record = service.getUserByUri(self._uri)

        if self._polarion_record is not None and not self._polarion_record.unresolvable:
            # parse all polarion attributes to this class
            for attr, value in self._polarion_record.__dict__.items():
                for key in value:
                    setattr(self, key, value[key])
        else:
            raise Exception(f'User not retrieved from Polarion')

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

    def __repr__(self):
        return f'{self.name} ({self.id})'

    def __str__(self):
        return f'{self.name} ({self.id})'


class UserCreator(Creator):
    def createFromUri(self, polarion, project, uri):
        return User(polarion, None, uri)

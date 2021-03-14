
class User(object):
    """
    A polarion user

    :param polarion: Polarion client object
    :param polarion_record: The user record

    """

    def __init__(self, polarion, polarion_record):
        self._polarion = polarion
        self._polarion_record = polarion_record

        # parse all polarion attributes to this class
        for attr, value in polarion_record.__dict__.items():
            for key in value:
                setattr(self, key, value[key])

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

    def __repr__(self):
        return f'{self.name} ({self.id})'

    def __str__(self):
        return f'{self.name} ({self.id})'

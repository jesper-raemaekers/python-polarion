class PolarionObject(object):
    def __init__(self, polarion, project, id=None, uri=None):
        self._polarion = polarion
        self._project = project
        self._id = id
        self._uri = uri

    def _reloadFromPolarion(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        elif name == 'id':
            return self._id
        elif name == 'uri':
            return self._uri
        else:
            super().__getattribute__(name)

    def beginTransaction(self):
        session = self._polarion.getService('Session')
        session.beginTransaction()

    def endTransaction(self, rollback=False):
        session = self._polarion.getService('Session')
        session.endTransaction(rollback=rollback)

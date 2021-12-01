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

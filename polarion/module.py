import copy
from .factory import createFromUri

class Module:
    def __init__(self, polarion, project, uri):
        """
        Create a Module.
        :param polarion: Polarion client object
        :param project: Polarion Project object
        :param uri: Polarion uri
        """
        self._uri = uri
        self._project = project
        self._polarion = polarion

        if self._uri is not None:
            service = self._polarion.getService('Tracker')
            self._prolarion_module = service.getModuleByUri(self._uri)

        self._buildFromPolarion()

    def _buildFromPolarion(self):
        if self._prolarion_module is not None and self._prolarion_module.unresolvable is False:
            self._original_polarion = copy.deepcopy(self._prolarion_module)
            for attr, value in self._prolarion_module.__dict__.items():
                for key in value:
                    setattr(self, key, value[key])

    def getWorkItemUris(self):
        """
        Get the uris of all workitems in the document.
        :return: string[]
        """
        service = self._polarion.getService('Tracker')
        workitems = service.getModuleWorkItemUris(self._uri, None, True)
        return workitems

    def getWorkItems(self):
        """
        Get all complete workitems.
        That may take some time on a large document.
        :return: Workitem[]
        """
        workitems = []
        workitem_uris = self.getWorkItemUris()
        for workitem_uri in workitem_uris:
            workitems.append(createFromUri(self._polarion, self._project, workitem_uri))
        return workitems

    def getTopLevelWorkitem(self):
        """
        Get the top level workitem, which is usually the title.
        :return: Workitem
        """
        return createFromUri(self._polarion, self._project, self.getWorkItemUris()[0])



    def __repr__(self):
        return f'Polarion module {self.title} in {self.moduleFolder}'

    def __str__(self):
        return f'Polarion module {self.title} in {self.moduleFolder}'

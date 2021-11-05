import copy

from .factory import createFromUri


class Document:
    def __init__(self, polarion, project, uri):
        """
        Create a Document.
        :param polarion: Polarion client object
        :param project: Polarion Project object
        :param uri: Polarion uri
        """
        self._uri = uri
        self._project = project
        self._polarion = polarion

        if self._uri is not None:
            service = self._polarion.getService('Tracker')
            self._polarion_document = service.getModuleByUri(self._uri)

        self._buildFromPolarion()

    def _buildFromPolarion(self):
        if self._polarion_document is not None and self._polarion_document.unresolvable is False:
            self._original_polarion = copy.deepcopy(self._polarion_document)
            for attr, value in self._polarion_document.__dict__.items():
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

    def createModule(self, name, location, allowed_workitem_types, structure_link_role):
        allowed_workitem_ids = []
        for allowed_workitem_type in allowed_workitem_types:
            allowed_workitem_ids.append(self._polarion.EnumOptionIdType(id=allowed_workitem_type))

        structure_link_role_id = self._polarion.EnumOptionIdType(id=structure_link_role)

        service = self._polarion.getService('Tracker')
        service.createaModule(self._project, location, name, allowed_workitem_ids, structure_link_role_id, False, None)

    def __repr__(self):
        return f'Polarion document {self.title} in {self.moduleFolder}'

    def __str__(self):
        return f'Polarion document {self.title} in {self.moduleFolder}'

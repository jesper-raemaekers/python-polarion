import copy

from .factory import createFromUri, Creator


class Document:
    def __init__(self, polarion, project, uri=None, location=None):
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
            if self._polarion_document is not None and self._polarion_document.unresolvable:
                raise Exception(
                    f'Cannot find document at URI {self._uri} in project {self._project.id}')

        elif location is not None:
            service = self._polarion.getService('Tracker')
            self._polarion_document = service.getModuleByLocation(self._project.id, location)
            if self._polarion_document is not None and self._polarion_document.unresolvable:
                raise Exception(
                    f'Cannot find document at location {location} in project {self._project.id}')
            self._uri = self._polarion_document.uri

        self._buildFromPolarion()

    def _buildFromPolarion(self):
        if self._polarion_document is not None and self._polarion_document.unresolvable is False:
            self._original_polarion = copy.deepcopy(self._polarion_document)
            for attr, value in self._polarion_document.__dict__.items():
                for key in value:
                    setattr(self, key, value[key])

    def _reloadFromPolarion(self):
        service = self._polarion.getService('Tracker')
        self._polarion_document = service.geModuleByUri(self._uri)
        self._buildFromPolarion()

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

    def addComment(self, title, comment, parent=None):
        """
        Adds a comment to the document.

        Throws an exception if the function is disabled in Polarion.

        :param title: Title of the comment (will be None for a reply)
        :param comment: The comment, may contain html
        :param parent: A parent comment, if none provided it's a root comment.
        """
        service = self._polarion.getService('Tracker')
        if hasattr(service, 'addComment'):
            if parent is None:
                parent = self._uri
            else:
                # force title to be empty, not allowed for reply comments
                title = None
            content = {
                'type': 'text/html',
                'content': comment,
                'contentLossy': False
            }
            service.addComment(parent, title, content)
            self._reloadFromPolarion()
        else:
            raise Exception("addComment binding not found in Trackter Service. Adding comments might be disabled.")

    def reuse(self, target_project_id, target_name, link_role, derived_fields=None):
        """
        Reuse this document in a different project.

        :param target_project_id: The target project id
        :param target_name: The target name
        :param link_role: The link role
        :param derived_fields: List of fields to be derived in the target document
        :return: The new document
        """
        if derived_fields is None:
            # TODO: Which are the default derived fields?
            derived_fields = ['id', 'description']
        service = self._polarion.getService('Tracker')
        new_uri = service.reuseModule(self._uri, target_project_id, None, target_name, link_role, None, None, derived_fields)
        return createFromUri(self._polarion, self._project, new_uri)

    def update(self, revision, auto_suspect):
        """
        Update a reused document to a revision of the source document.

        :param revision: Source document revision
        :param auto_suspect: If set to True, changed workitems will mark their links as suspect
        """
        service = self._polarion.getService('Tracker')
        service.updateDerivedDocument(self._uri, revision, auto_suspect)

    def save(self):
        """
        Update the document in polarion
        """
        updated_item = {}

        for attr, value in self._polarion_document.__dict__.items():
            for key in value:
                current_value = getattr(self, key)
                prev_value = getattr(self._original_polarion, key)
                if current_value != prev_value:
                    updated_item[key] = current_value
        if len(updated_item) > 0:
            updated_item['uri'] = self._uri
            service = self._polarion.getService('Tracker')
            service.updateModule(updated_item)
            self._reloadFromPolarion()

    def __repr__(self):
        return f'Polarion document {self.title} in {self.moduleFolder}'

    def __str__(self):
        return f'Polarion document {self.title} in {self.moduleFolder}'


class DocumentCreator(Creator):
    def createFromUri(self, polarion, project, uri):
        return Document(polarion, project, uri)

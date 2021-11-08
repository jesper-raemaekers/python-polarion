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

    def getWorkitemUris(self):
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
        workitem_uris = self.getWorkitemUris()
        for workitem_uri in workitem_uris:
            workitems.append(createFromUri(self._polarion, self._project, workitem_uri))
        return workitems

    def getTopLevelWorkitem(self):
        """
        Get the top level workitem, which is usually the title.
        :return: Workitem
        """
        return createFromUri(self._polarion, self._project, self.getWorkitemUris()[0])

    def insertComment(self, text):
        """
        Inserts a comment with no reference to a workitem. Only shows up in the comment list if unreferenced comments
        are enabled there.
        :param text:
        :return:
        """
        service = self._polarion.getService('Tracker')
        service.createDocumentComment(self._uri, self._polarion.TextType(
            content=text, type='text/html', contentLossy=False))

    def insertCommentAtWorkitem(self, workitem, text):
        """
        Inserts a comment with reference to a workitem.
        :param text:
        :return:
        """
        service = self._polarion.getService('Tracker')
        service.createDocumentCommentReferringWI(self._uri, workitem.uri, self._polarion.TextType(
            content=text, type='text/html', contentLossy=False))

    def insertCommentReply(self, comment_uri, text):
        """
        Inserts a comment with reference to a workitem.
        :param text:
        :return:
        """
        service = self._polarion.getService('Tracker')
        service.createDocumentCommentReply(comment_uri, self._polarion.TextType(
            content=text, type='text/html', contentLossy=False))

    def add_heading(self, title, parent_workitem=None):
        heading = self._project.createWorkitem('heading')
        heading.title = title
        heading.save()
        heading.moveToDocument(self, parent_workitem)
        return heading

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

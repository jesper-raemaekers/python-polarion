import copy

from zeep import xsd

from .factory import createFromUri, Creator


class Document:
    def __init__(self, polarion, project, uri=None, location=None):
        """
        Create a Document.
        :param polarion: Polarion client object
        :param project: Polarion Project object
        :param uri: Polarion uri (first possibility to get a document)
        :param location: Document location (second possibility to get a document)
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
        self._polarion_document = service.getModuleByUri(self._uri)
        self._buildFromPolarion()

    def getWorkitemUris(self):
        """
        Get the uris of all workitems in the document.
        :return: string[]
        """
        service = self._polarion.getService('Tracker')
        workitems = service.getModuleWorkItemUris(self._uri, None, True)
        return workitems

    def getWorkitems(self):
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

    def getChildren(self, workitem):
        """
        Gets the children of a workitem in the document.

        :param workitem: Workitem to get children for
        :return: List of workitems
        """
        workitem_children = []
        if workitem.linkedWorkItemsDerived is not None:
            document_uris = self.getWorkitemUris()
            children = (w for w in workitem.linkedWorkItemsDerived.LinkedWorkItem if w.role.id == self.structureLinkRole.id and w.workItemURI in document_uris)
            for child in children:
                workitem_children.append(createFromUri(self._polarion, self._project, child.workItemURI))
        return workitem_children

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
            raise Exception("addComment binding not found in Tracker Service. Adding comments might be disabled.")

    def addHeading(self, title, parent_workitem=None):
        """
        Adds a heading to a document

        :param title: Title of the heading
        :param parent_workitem: Parent workitem in the document hierarchy, set to None to create it on top level
        :return: Heading workitem
        """
        heading = self._project.createWorkitem('heading')
        heading.title = title
        heading.save()
        heading.moveToDocument(self, parent_workitem)
        return heading

    def reuse(self, target_project_id, target_location, target_name, target_title, link_role='derived_from', derived_fields=None):
        """
        Reuse this document in a different project.

        :param target_project_id: The target project id
        :param target_location: Location of the target document
        :param target_name: The target document's name
        :param target_title: Title of the target document
        :param link_role: Link role of the derived documents
        :param derived_fields: List of fields to be derived in the target document
        :return: The new document
        """
        if derived_fields is None:
            derived_fields = ['title', 'description']
        service = self._polarion.getService('Tracker')
        new_uri = service.reuseDocument(self._uri, target_project_id, target_location, target_name, target_title, True, link_role, derived_fields)
        return createFromUri(self._polarion, self._project, new_uri)

    def update(self, revision=None, auto_suspect=False):
        """
        Update a reused document to a revision of the source document.

        :param revision: Source document revision
        :param auto_suspect: If set to True, changed workitems will mark their links as suspect
        """
        service = self._polarion.getService('Tracker')
        service.updateDerivedDocument(self._uri, revision if revision is not None else xsd.const.Nil, auto_suspect)

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

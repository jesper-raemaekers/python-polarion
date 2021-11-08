from .factory import createFromUri
from .workitem import Workitem
from .testrun import Testrun
from .user import User
from .plan import Plan
from .document import Document


class Project(object):
    """
    A Polarion project instance usable to access workitem, testruns and more. usually create by using the Polarion client.

    :param polarion: The polarion client instance
    :param project_id: The project id, as can be found in the URL of the project

    """

    def __init__(self, polarion, project_id):
        self.polarion = polarion
        self.id = project_id

        # get details from polarion on this project
        service = self.polarion.getService('Project')
        try:
            self.polarion_data = service.getProject(self.id)
        except Exception:
            raise Exception(f'Could not find project {project_id}')

        if 'name' in self.polarion_data and not self.polarion_data.unresolvable:
            # succeeded
            self.name = self.polarion_data.name
            self.tracker_prefix = self.polarion_data.trackerPrefix
        else:
            raise Exception(f'Could not find project {project_id}')

    def getUsers(self):
        """
        Gets all users in this project
        """
        users = []
        service = self.polarion.getService('Project')
        project_users = service.getProjectUsers(self.id)
        for user in project_users:
            users.append(User(self.polarion, user))
        return users

    def findUser(self, name):
        """
        Find a specific user by id or name in this project
        """
        project_users = self.getUsers()
        for user in project_users:
            if user.id.lower() == name.lower() or user.name.lower() == name.lower():
                return user
        return None

    def getWorkitem(self, id: str):
        """Get a workitem by string

        :param id: The ID of the project workitem (PREF-123).
        :return: The request workitem
        :rtype: Workitem
        """
        return Workitem(self.polarion, self, id)

    def getPlan(self, id: str):
        """Get a plan by string

        :param id: The ID of the project plan.
        :return: The request plan
        :rtype: Plan
        """
        return Plan(self.polarion, self, id=id)

    def createPlan(self, new_plan_name, new_plan_id, new_plan_template, new_plan_parent=None):
        return Plan(self.polarion, self, new_plan_name=new_plan_name, new_plan_id=new_plan_id, new_plan_template=new_plan_template,
                    new_plan_parent=new_plan_parent)

    def createWorkitem(self, workitem_type: str):
        return Workitem(self.polarion, self, new_workitem_type=workitem_type)

    def searchWorkitem(self, query='', order='Created', field_list=None, limit=-1):
        """Query for available workitems. This will only query for the items.
        If you also want the Workitems to be retrieved, used searchWorkitemFullItem.
        
        :param query: The query to use while searching
        :param order: Order by
        :param field_list: list of fields to retrieve for each search result
        :param limit: The limit of workitems, -1 for no limit
        :return: The search results
        :rtype: Workitem[] but only with the given fields set
        """
        if field_list is None:
            field_list = ['id']

        query += f' AND project.id:{self.id}'
        service = self.polarion.getService('Tracker')
        return service.queryWorkItemsLimited(
            query, order, field_list, limit)

    def searchWorkitemFullItem(self, query='', order='Created', limit=-1):
        """Query for available workitems. This will query for the items and then fetch all result. May take a while for a big search with many results.

        :param query: The query to use while searching
        :param order: Order by
        :param limit: The limit of workitems, -1 for no limit
        :return: The search results
        :rtype: Workitem[]
        """
        return_list = []
        workitems = self.searchWorkitem(query, order, ['id'], limit)
        for workitem in workitems:
            return_list.append(
                Workitem(self.polarion, self, workitem.id))
        return return_list

    def getTestRun(self, id: str):
        """Get a testrun by string

        :param id: The ID of the project testrun.
        :return: The request testrun
        :rtype: Testrun
        """
        return Testrun(self.polarion, f'subterra:data-service:objects:/default/{self.id}${{TestRun}}{id}')

    def searchTestRuns(self, query='', order='Created', limit=-1):
        """Query for available test runs

        :param query: The query to use while searching
        :param order: Order by
        :param limit: The limit of test runs, -1 for no limit
        :return: The request testrun
        :rtype: Testrun[]
        """
        if len(query) > 0:
            query += ' AND '
        query += f'project.id:{self.id}'
        return_list = []
        service = self.polarion.getService('TestManagement')
        test_runs = service.searchTestRunsLimited(query, order, limit)
        for test_run in test_runs:
            return_list.append(
                Testrun(self.polarion, polarion_test_run=test_run))
        return return_list

    def createTestRun(self, id, title, template_id):
        """
        Create a new test run with specified title from an existing test run template
        :param id: 
        :param title: 
        :param template_id: 
        """
        service = self.polarion.getService('TestManagement')
        new_testrun_uri = service.createTestRunWithTitle(self.id, id, title, template_id)
        return createFromUri(self.polarion, self, new_testrun_uri)

    def getEnum(self, enum_name):
        """Get the options for a selected enumeration

        :param enum_name: The first part of the enum name. Will be postpended by -enum.xml by Polarion API
        :return: A list of options for the enum
        :rtype: string[]
        """
        available = []
        service = self.polarion.getService('Tracker')
        av = service.getAllEnumOptionsForId(self.id, enum_name)
        for a in av:
            if a.id not in available:
                available.append(a.id)
        return available

    def createDocument(self, location, name, title, allowed_workitem_types, structure_link_role, home_page_content=''):
        """
        Creates a new document

        :param location: Document location, the default location is _default
        :param name: Name of the document
        :param title: Document title
        :param allowed_workitem_types: List of workitem types to be allowed inside the document
        :param structure_link_role: Link role to be used when defining the document hierarchy between parents and children
        :param home_page_content: Initial content of the document as HTML
        :return: New document
        """
        allowed_workitem_ids = []
        for allowed_workitem_type in allowed_workitem_types:
            allowed_workitem_ids.append(self.polarion.EnumOptionIdType(id=allowed_workitem_type))

        structure_link_role_id = self.polarion.EnumOptionIdType(id=structure_link_role)

        service = self.polarion.getService('Tracker')
        uri = service.createDocument(self.id, location, name, title, allowed_workitem_ids, structure_link_role_id, home_page_content)
        return Document(self.polarion, self, uri)

    def getDocumentSpaces(self):
        """
        Get a list al all document spaces.
        :return:string[]
        """
        service = self.polarion.getService('Tracker')
        spaces = service.getDocumentSpaces(self.id)
        return sorted(spaces)

    def getDocumentLocations(self):
        """
        Get a list of all document locations.
        :return:string[]
        """
        service = self.polarion.getService('Tracker')
        locations = service.getDocumentLocations(self.id)
        return sorted(locations)

    def getDocumentsInSpace(self, space):
        """
        Get all documents in a space.
        :param space: Name of the space.
        :return: Document[]
        """
        documents = []
        service = self.polarion.getService('Tracker')
        uris = service.getModuleUris(self.id, space)
        for uri in uris:
            documents.append(Document(self.polarion, self, uri=uri))
        return documents

    def getDocument(self, location):
        """
        Get a document by location.

        :param location: Location of the document.
        :return: Document
        """
        return Document(self.polarion, self, location=location)

    def __repr__(self):
        return f'Polarion project {self.name} prefix {self.tracker_prefix}'

    def __str__(self):
        return f'Polarion project {self.name} prefix {self.tracker_prefix}'

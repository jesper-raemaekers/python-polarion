from zeep import Client
from zeep.plugins import HistoryPlugin
from lxml.etree import Element
from lxml import etree
import requests
import re
from urllib.parse import urljoin

from .workitem import Workitem
from .testrun import Testrun
from .user import User


class Project(object):
    """
    A Polarion project instance usable to access workitem, testruns and more. usually create by using the Polarion client.

    :param polarion: The polarion client instance
    :param project_id: The project id, as can be found in the URL of the project

    """

    def __init__(self, polarion, project_id):
        self.polarion = polarion
        self.id = project_id

        # get detaisl from polarion on this project
        service = self.polarion.getService('Project')
        try:
            self.polarion_data = service.getProject(self.id)
        except:
            raise Exception(f'Could not find project {project_id}')

        if 'name' in self.polarion_data and self.polarion_data.unresolvable == False:
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

    def createWorkitem(self, workitem_type: str):
        return Workitem(self.polarion, self, new_workitem_type=workitem_type)

    def searchWorkitemFullItem(self, query='', order='Created', limit=-1):
        """Query for available workitems. This will query for the items and then fetch all result. May take a while for a big search with many results.

        :param query: The query to use while searching
        :param order: Order by
        :param limit: The limit of workitems, -1 for no limit
        :return: The search results
        :rtype: Workitem[]
        """
        query += f' AND project.id:{self.id}'
        return_list = []
        service = self.polarion.getService('Tracker')
        workitems = service.queryWorkItemsLimited(
            query, order, ['id'], limit)
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

    def __repr__(self):
        return f'Polarion project {self.name} prefix {self.tracker_prefix}'

    def __str__(self):
        return f'Polarion project {self.name} prefix {self.tracker_prefix}'

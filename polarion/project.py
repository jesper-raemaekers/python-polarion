from zeep import Client
from zeep.plugins import HistoryPlugin
from lxml.etree import Element
from lxml import etree
import requests
import re
from urllib.parse import urljoin

from .workitem import Workitem
from .testrun import Testrun


class Project(object):

    def __init__(self, polarion, project_id):
        self.polarion = polarion
        self.id = project_id

        # get detaisl from polarion on this project
        service = self.polarion.getService('Project')
        try:
            self.polarion_data = service.getProject(self.id)
        except:
            raise Exception(f'Could not find project {project_id}')

        if 'name' in self.polarion_data:
            # succeeded
            self.name = self.polarion_data.name
            self.tracker_prefix = self.polarion_data.trackerPrefix
        else:
            raise Exception(f'Could not find project {project_id}')

    def getWorkitem(self, id: str):
        return Workitem(self.polarion, self, id)

    def getTestRun(self, id: str):
        return Testrun(self.polarion, f'subterra:data-service:objects:/default/{self.id}${{TestRun}}{id}')

    def searchTestRuns(self, query='', order='Created', limit=-1):
        return_list = []
        service = self.polarion.getService('TestManagement')
        test_runs = service.searchTestRunsLimited(query, order, limit)
        for test_run in test_runs:
            return_list.append(
                Testrun(self.polarion, polarion_test_run=test_run))
        return return_list

    def getEnum(self, enum_name):
        available = []
        service = self.polarion.getService('Tracker')
        av = service.getAllEnumOptionsForId(self.id, enum_name)
        for a in av:
            available.append(a.id)
        return available

    def __repr__(self):
        if self.polarion_data:
            return f'Polarion project {self.name} prefix {self.tracker_prefix}'
        else:
            return f'Polarion project {self.name}'

    def __str__(self):
        if self.polarion_data:
            return f'Polarion project {self.name} prefix {self.tracker_prefix}'
        else:
            return f'Polarion project {self.name}'

from zeep import Client
from zeep.plugins import HistoryPlugin
from lxml.etree import Element
from lxml import etree
import requests
import re
from urllib.parse import urljoin
from .record import Record

class Testrun(object):

    def __init__(self, polarion, project, id):
        self.polarion = polarion
        self.project = project
        self.id = id

        service = self.polarion.getService('TestManagement')

        try:
            self.polarion_test_run = service.getTestRunById(self.project.id, self.id)
        except:
            raise Exception(f'Cannot find test run {self.id} in project {self.project.id}')

        if self.polarion_test_run:
            self.title = self.polarion_test_run.title
            self.status = self.polarion_test_run.status.id
            self.created = self.polarion_test_run.created
            self.updated = self.polarion_test_run.updated
            self.updated = self.polarion_test_run.finishedOn
            self.uri = self.polarion_test_run.uri
            self.records = []
            for r in self.polarion_test_run.records.TestRecord:
                self.records.append(Record(self.polarion, self.project, self, r))
            #TODO: parse test records

    def __repr__(self):
        return f'Testrun {self.id} ({self.title})'

    def __str__(self):
        return f'Testrun {self.id} ({self.title})'


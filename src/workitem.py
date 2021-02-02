from zeep import Client
from zeep.plugins import HistoryPlugin
from lxml.etree import Element
from lxml import etree
import requests
import re
from urllib.parse import urljoin

class Workitem(object):

    def __init__(self, polarion, project, id, uri = None):
        self.polarion = polarion
        self.project = project
        self.id = id
        self.uri = uri

        service = self.polarion.getService('Tracker')

        if self.uri:
            try:
                self.polarion_item = service.getWorkItemByUri(self.uri)
                self.id = self.polarion_item.id
            except:
                raise Exception(f'Cannot find workitem {self.id} in project {self.project.id}')
        else:
            try:
                self.polarion_item = service.getWorkItemById(self.project.id, self.id)
            except:
                raise Exception(f'Cannot find workitem {self.id} in project {self.project.id}')

        if self.polarion_item:
            self.title = self.polarion_item.title
            self.status = self.polarion_item.status.id
            self.severity = self.polarion_item.severity.id
            self.priority = self.polarion_item.priority.id
            self.type = self.polarion_item.type.id
            self.created = self.polarion_item.created
            self.updated = self.polarion_item.updated
            if self.polarion_item.description:
                self.description = self.polarion_item.description.content
            self.author = {'name': self.polarion_item.author.name, 'email': self.polarion_item.author.email, 'id':self.polarion_item.author.id}
            self.uri = self.polarion_item.uri

            self.is_test = False
            for field in self.polarion_item.customFields.Custom:
                if field.key == 'testType':
                    self.is_test = True

        if self.is_test:
            service = self.polarion.getService('TestManagement')
            try:
                self.polarion_test = service.getTestSteps(self.uri)
            except:
                raise Exception('Cannot get test properties of object that is a test item')
            if self.polarion_test:
                pass
            #parse test steps to some sort of value

    def __repr__(self):
        return f'Workitem ({self.type}) {self.id} ({self.title})'

    def __str__(self):
        return f'Workitem ({self.type}) {self.id} ({self.title})'


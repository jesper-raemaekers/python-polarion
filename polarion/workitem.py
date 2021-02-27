from zeep import Client
from zeep.plugins import HistoryPlugin
from lxml.etree import Element
from lxml import etree
import copy
import requests
import re
from urllib.parse import urljoin
from enum import Enum


class Workitem(object):
    class HyperlinkRoles(Enum):
        INTERNAL_REF = 'internal reference'
        EXTERNAL_REF = 'external reference'

    def __init__(self, polarion, project, id, uri=None):
        self._polarion = polarion
        self._project = project
        self._id = id
        self._uri = uri

        service = self._polarion.getService('Tracker')
        service_test = self._polarion.getService('TestManagement')

        if self._uri:
            try:
                self._polarion_item = service.getWorkItemByUri(self._uri)
                self._id = self._polarion_item.id
            except:
                raise Exception(
                    f'Cannot find workitem {self._id} in project {self._project.id}')
        else:
            try:
                self._polarion_item = service.getWorkItemById(
                    self._project.id, self._id)
            except:
                raise Exception(
                    f'Cannot find workitem {self._id} in project {self._project.id}')

        if self._polarion_item != None:
            self._original_polarion = copy.deepcopy(self._polarion_item)
            for attr, value in self._polarion_item.__dict__.items():
                for key in value:
                    setattr(self, key, value[key])
            self._polarion_test_steps = None
            try:
                self._polarion_test_steps = service_test.getTestSteps(self.uri)
            except:
                # fail silently as there are probably not test steps for this workitem
                pass
            self._parsed_test_steps = None
            if self._polarion_test_steps != None:
                if self._polarion_test_steps.keys != None and self._polarion_test_steps.steps:
                    # oh god, parse the test steps...
                    columns = []
                    self._parsed_test_steps = []
                    for col in self._polarion_test_steps.keys.EnumOptionId:
                        columns.append(col.id)
                    # now parse the rows
                    for row in self._polarion_test_steps.steps.TestStep:
                        current_row = {}
                        for col_id in range(len(row.values.Text)):
                            current_row[columns[col_id]
                                        ] = row.values.Text[col_id].content
                        self._parsed_test_steps.append(current_row)

    def getVailableStatus(self):
        available_status = []
        service = self._polarion.getService('Tracker')
        av_status = service.getAvailableEnumOptionIdsForId(self.uri, 'status')
        for status in av_status:
            available_status.append(status.id)
        return available_status

    def setStatus(self, status):
        if status in self.getVailableStatus():
            self.status.id = status
            self.save()

    def getDescription(self):
        """
        Get a comment if available. The comment may contain HTML if edited in Polarion!
        """
        if self.description != None:
            return self.description.content
        return None

    def setDescription(self, description):
        self.description = {
            'type': 'text/html',
            'content': description,
            'contentLossy': False
        }
        self.save()

    def hasTestSteps(self):
        if self._parsed_test_steps != None:
            return len(self._parsed_test_steps) > 0
        return False

    def addComment(self, title, comment, parent=None):
        service = self._polarion.getService('Tracker')
        if parent == None:
            parent = self.uri
        else:
            # force title to be empty, not allowed for reply comments
            title = None
        content = {
            'type': 'text/html',
            'content': comment,
            'contentLossy': False
        }
        service.addComment(parent, title, content)

    def addHyperlink(self, url, hyperlink_type: HyperlinkRoles):
        service = self._polarion.getService('Tracker')
        service.addHyperlink(self.uri, url, {'id': hyperlink_type.value})

    def save(self):
        updated_item = {}
        # orig_work_item = self._polarion_item

        for attr, value in self._polarion_item.__dict__.items():
            for key in value:
                current_value = getattr(self, key)
                prev_value = getattr(self._original_polarion, key)
                if current_value != prev_value:
                    updated_item[key] = current_value
        if len(updated_item) > 0:
            updated_item['uri'] = self.uri
            service = self._polarion.getService('Tracker')
            service.updateWorkItem(updated_item)
            self._original_polarion = copy.deepcopy(self._polarion_item)

    def __repr__(self):
        return f'Workitem ({self.type.id}) {self._id} ({self.title})'

    def __str__(self):
        return f'Workitem ({self.type.id}) {self._id} ({self.title})'

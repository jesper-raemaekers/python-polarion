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
    """
    Create a Polarion workitem object either from and id or from an Polarion uri.

    :param polarion: Polarion client object
    :param project: Polarion Project object
    :param id: Workitem ID
    :param uri: Polarion uri

    """
    class HyperlinkRoles(Enum):
        """
        Hyperlink reference type enum
        """
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
            if self._polarion_item.unresolvable == True:
                raise Exception(f'Workitem unresolvable')
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

    def getStatusEnum(self):
        """
        tries to get the status enum of this workitem type
        When it fails to get it, the list will be empty

        :return: An array of strings of the statusses
        :rtype: string[]
        """
        try:
            enum = self._project.getEnum(f'{self.type.id}-status')
            return enum
        except:
            return []

    def getResolutionEnum(self):
        """
        tries to get the resolution enum of this workitem type
        When it fails to get it, the list will be empty

        :return: An array of strings of the resolutions
        :rtype: string[]
        """
        try:
            enum = self._project.getEnum(f'{self.type.id}-resolution')
            return enum
        except:
            return []

    def getSeverityEnum(self):
        """
        tries to get the severity enum of this workitem type
        When it fails to get it, the list will be empty

        :return: An array of strings of the severities
        :rtype: string[]
        """
        try:
            enum = self._project.getEnum(f'{self.type.id}-severity')
            return enum
        except:
            return []

    def getAvailableStatus(self):
        """
        Get all available status option for this workitem

        :return: An array of string of the statusses
        :rtype: string[]
        """
        available_status = []
        service = self._polarion.getService('Tracker')
        av_status = service.getAvailableEnumOptionIdsForId(self.uri, 'status')
        for status in av_status:
            available_status.append(status.id)
        return available_status

    def getAvailableActionsDetails(self):
        """
        Get all actions option for this workitem with defails

        :return: An array of dictionaries of the actions
        :rtype: dict[]
        """
        available_actions = []
        service = self._polarion.getService('Tracker')
        av_actions = service.getAvailableActions(self.uri)
        for action in av_actions:
            available_actions.append(action)
        return available_actions

    def getAvailableActions(self):
        """
        Get all actions option for this workitem without details

        :return: An array of strings of the actions
        :rtype: string[]
        """
        available_actions = []
        service = self._polarion.getService('Tracker')
        av_actions = service.getAvailableActions(self.uri)
        for action in av_actions:
            available_actions.append(action.nativeActionId)
        return available_actions

    def preformAction(self, action_name):
        """
        Preform selected action. An exception will be thorn if some prerequisite is not set.

        :param action_name: string containing the action name
        """
        # get id from action name
        service = self._polarion.getService('Tracker')
        av_actions = service.getAvailableActions(self.uri)
        for action in av_actions:
            if action.nativeActionId == action_name or action.actionName == action_name:
                service.performWorkflowAction(self.uri, action.actionId)

    def preformActionId(self, actionId: int):
        """
        Preform selected action. An exception will be thorn if some prerequisite is not set.

        :param actionId: number for the action to preform
        """
        service = self._polarion.getService('Tracker')
        service.performWorkflowAction(self.uri, action)

    def setStatus(self, status):
        """
        Sets the status opf the workitem and saves the workitem, not respecting any project configured limits or requirements.

        :param status: name of the status
        """
        if status in self.getVailableStatus():
            self.status.id = status
            self.save()

    def getDescription(self):
        """
        Get a comment if available. The comment may contain HTML if edited in Polarion!

        :return: The content of the description, may contain HTML
        :rtype: string
        """
        if self.description != None:
            return self.description.content
        return None

    def setDescription(self, description):
        """
        Sets the description and saves the workitem

        :param description: the description
        """
        self.description = {
            'type': 'text/html',
            'content': description,
            'contentLossy': False
        }
        self.save()

    def hasTestSteps(self):
        """
        Checks if the workitem has test steps

        :return: True/False
        :rtype: boolean
        """
        if self._parsed_test_steps != None:
            return len(self._parsed_test_steps) > 0
        return False

    def addComment(self, title, comment, parent=None):
        """
        Adds a comment to the workitem.

        :param title: Title of the comment (will be None for a reply)
        :param comment: The comment, may contain html
        :param parent: A parent comment, if none provided it's a root comment.
        """
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
        """
        Adds a hyperlink to the workitem.

        :param url: The URL to add
        :param hyperlink_type: Select internal or external hyperlink
        """
        service = self._polarion.getService('Tracker')
        service.addHyperlink(self.uri, url, {'id': hyperlink_type.value})

    def save(self):
        """
        Update the workitem in polarion
        """
        updated_item = {}

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
        return f'{self._id}: {self.title}'

    def __str__(self):
        return f'{self._id}: {self.title}'

from zeep import Client
from zeep.plugins import HistoryPlugin
from lxml.etree import Element
from lxml import etree
import requests
import re
from urllib.parse import urljoin
from .record import Record
from .factory import Creator


class Testrun(object):
    """
    Create a Polarion testrun object from uri or directly with Polarion content

    :param polarion: Polarion client object
    :param uri: Polarion uri
    :param polarion_test_run: The data from Polarion of this testrun

    :ivar records: An array of :class:`.Record`
    """

    def __init__(self, polarion, uri=None, polarion_test_run=None):
        self._polarion = polarion

        if uri != None:
            service = self._polarion.getService('TestManagement')
            try:
                self._polarion_test_run = service.getTestRunByUri(uri)
            except:
                raise Exception(f'Cannot find test run {uri}')

        elif polarion_test_run != None:
            self._polarion_test_run = polarion_test_run
        else:
            raise Exception(f'Provide either an uri or polarion_test_run ')

        if self._polarion_test_run != None:
            for attr, value in self._polarion_test_run.__dict__.items():
                for key in value:
                    if key == 'records':
                        setattr(self, '_'+key, value[key])
                    else:
                        setattr(self, key, value[key])

        self.records = []
        if self._records != None:
            for r in self._records.TestRecord:
                self.records.append(
                    Record(self._polarion, self, r))

    def __repr__(self):
        return f'Testrun {self.id} ({self.title}) created {self.created}'

    def __str__(self):
        return f'Testrun {self.id} ({self.title}) created {self.created}'

class TestrunCreator(Creator):
    def createFromUri(self, polarion, project, uri):
        return Testrun(polarion, uri)
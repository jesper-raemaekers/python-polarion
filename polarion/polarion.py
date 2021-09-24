from zeep import Client
from zeep.plugins import HistoryPlugin
from lxml.etree import Element
from lxml import etree
import requests
import re
from urllib.parse import urljoin
from .project import Project
import atexit

_baseServiceUrl = 'ws/services'


class Polarion(object):
    """
    Create a Polarion client which communicates to the Polarion server.

    :param polarion_url: The base URL for the polarion instance. For example http://example/com/polarion
    :param user: The user name to login
    :param password: The password for that user
    :param static_service_list: Set to True when this class may not use a request to get the services list

    """

    def __init__(self, polarion_url, user, password, static_service_list=False):
        self.user = user
        self.password = password
        self.url = polarion_url

        self.services = {}

        if not self.url.endswith('/'):
            self.url += '/'
        self.url = urljoin(self.url, _baseServiceUrl)

        if static_service_list == True:
            self._getStaticServices()
        else:
            self._getServices()
        self._createSession()
        self._getTypes()

        atexit.register(self._atexit_cleanup)
        
    def _atexit_cleanup(self):
        """
        Cleanup function to logout when Python is shutting down.
        :return: None
        """
        self.services['Session']['client'].service.endSession()

    def _getStaticServices(self):
        default_services = ['Session', 'Project', 'Tracker',
                            'Builder', 'Planning', 'TestManagement', 'Security']
        service_base_url = self.url + '/'
        for service in default_services:
            self.services[service] = {'url': urljoin(
                service_base_url, service + 'WebService')}

    def _getServices(self):
        """
        Parse the list of services available in the overview
        """
        service_overview = requests.get(self.url)
        service_base_url = self.url + '/'
        if service_overview.ok:
            services = re.findall("(\w+)WebService", service_overview.text)
            for service in services:
                if service not in self.services:
                    self.services[service] = {'url': urljoin(
                        service_base_url, service + 'WebService')}

    def _createSession(self):
        """
        Starts a session with the specified user/password
        """
        if 'Session' in self.services:
            self.history = HistoryPlugin()
            self.services['Session']['client'] = Client(
                self.services['Session']['url'] + '?wsdl', plugins=[self.history])
            try:
                self.sessionHeaderElement = None
                self.services['Session']['client'].service.logIn(
                    self.user, self.password)
                tree = self.history.last_received['envelope'].getroottree()
                self.sessionHeaderElement = tree.find(
                    './/{http://ws.polarion.com/session}sessionID')
            except:
                raise Exception(
                    f'Could not log in to Polarion for user {self.user}')
            if self.sessionHeaderElement is not None:
                self._updateServices()
        else:
            raise Exception(
                'Cannot login because WSDL has no SessionWebService')

    def _updateServices(self):
        """
        Updates all services with the correct session ID
        """
        if self.sessionHeaderElement == None:
            raise Exception('Cannot update services when not logged in')
        for service in self.services:
            if service != 'Session':
                if 'client' not in service:
                    self.services[service]['client'] = Client(
                        self.services[service]['url'] + '?wsdl')
                self.services[service]['client'].set_default_soapheaders(
                    [self.sessionHeaderElement])
            if service == 'Tracker':
                if hasattr(self.services[service]['client'].service, 'addComment'):
                    # allow addComment to be send without title, needed for reply comments
                    self.services[service]['client'].service.addComment._proxy._binding.get(
                        'addComment').input.body.type._element[1].nillable = True
            if service == 'Planning':
                self.services[service]['client'].service.createPlan._proxy._binding.get(
                        'createPlan').input.body.type._element[3].nillable = True

    def _getTypes(self):
        # TODO: check if the namespace is always the same
        self.EnumOptionIdType = self.getTypeFromService('TestManagement', 'ns3:EnumOptionId')
        self.TextType = self.getTypeFromService('TestManagement', 'ns1:Text')
        self.ArrayOfTestStepResultType = self.getTypeFromService('TestManagement', 'ns4:ArrayOfTestStepResult')
        self.TestStepResultType = self.getTypeFromService('TestManagement', 'ns4:TestStepResult')
        self.WorkItemType = self.getTypeFromService('Tracker', 'ns2:WorkItem')
        self.LinkedWorkItemType = self.getTypeFromService('Tracker', 'ns2:LinkedWorkItem')
        self.LinkedWorkItemArrayType = self.getTypeFromService('Tracker', 'ns2:ArrayOfLinkedWorkItem')
        self.ArrayOfCustomType = self.getTypeFromService('Tracker', 'ns2:ArrayOfCustom')
        self.CustomType = self.getTypeFromService('Tracker', 'ns2:Custom')
        self.ArrayOfEnumOptionIdType = self.getTypeFromService('Tracker', 'ns2:ArrayOfEnumOptionId')
        self.ArrayOfSubterraURIType = self.getTypeFromService('Tracker', 'ns1:ArrayOfSubterraURI')

    def hasService(self, name: str):
        """
        Checks if a WSDL service is available
        """
        if name in self.services:
            return True
        return False

    def getService(self, name: str):
        """
        Get a WSDL service client. The name can be 'Trakcer' or 'Session'
        """
        # request user info to see if we're still logged in
        try:
            _user = self.services['Project']['client'].service.getUser(self.user)
        except:
            # if not, create a new session
            self._createSession()

        if name in self.services:
            return self.services[name]['client'].service
        else:
            raise Exception('Service does not exsist')

    def getTypeFromService(self, name: str, type_name):
        """
        """
        if name in self.services:
            return self.services[name]['client'].get_type(type_name)
        else:
            raise Exception('Service does not exsist')

    def getProject(self, project_id):
        """Get a Polarion project

        :param project_id: The ID of the project.
        :return: The request project
        :rtype: Project
        """
        return Project(self, project_id)

    def __repr__(self):
        return f'Polarion client for {self.url} with user {self.user}'

    def __str__(self):
        return f'Polarion client for {self.url} with user {self.user}'

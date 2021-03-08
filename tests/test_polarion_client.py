import unittest
from polarion.polarion import Polarion
from keys import polarion_user, polarion_password, polarion_url
from time import sleep
import mock


class TestPolarionClient(unittest.TestCase):

    def test_wrong_url(self):
        url = polarion_url + '/wrong'
        self.assertRaises(Exception, Polarion.__init__, url,
                          polarion_user, polarion_password)

    def test_wrong_user(self):
        user = polarion_user + 'incorrect'
        self.assertRaises(Exception, Polarion.__init__, polarion_url,
                          user, polarion_password)

    def test_wrong_password(self):
        password = polarion_password + 'incorrect'
        self.assertRaises(Exception, Polarion.__init__, polarion_url,
                          polarion_user, password)

    def test_available_services_static(self):
        known_services = ['Session', 'Project', 'Tracker',
                          'Builder', 'Planning', 'TestManagement', 'Security']

        pol = Polarion(polarion_url, polarion_user,
                       polarion_password, static_service_list=True)

        for service in known_services:
            self.assertTrue(pol.hasService(service),
                            msg='Service should exist')

        self.assertFalse(pol.hasService('made_up'),
                         msg='Service should not exist')

    def test_available_services(self):
        known_services = ['Session', 'Project', 'Tracker',
                          'Builder', 'Planning', 'TestManagement', 'Security']

        pol = Polarion(polarion_url, polarion_user, polarion_password)

        for service in known_services:
            self.assertTrue(pol.hasService(service),
                            msg='Service should exist')

        self.assertFalse(pol.hasService('made_up'),
                         msg='Service should not exist')

    def test_services(self):
        known_services = ['Tracker', 'TestManagement']

        pol = Polarion(polarion_url, polarion_user, polarion_password)

        for service in known_services:
            s = pol.getService(service)
            # print(s)
            self.assertGreater(len(s.__dir__()), 10)

    def test_types(self):
        pol = Polarion(polarion_url, polarion_user, polarion_password)
        self.assertIn('EnumOptionId', str(type(pol.EnumOptionIdType)))
        self.assertIn('Text', str(type(pol.TextType)))
        self.assertIn('ArrayOfTestStepResult',
                      str(type(pol.ArrayOfTestStepResultType)))
        self.assertIn('TestStepResult', str(type(pol.TestStepResultType)))

    def test_type_wrong_service(self):
        pol = Polarion(polarion_url, polarion_user, polarion_password)

        self.assertRaises(Exception, pol.getTypeFromService, 'made_up',
                          'dont care')

    def test_string(self):
        pol = Polarion(polarion_url, polarion_user, polarion_password)

        self.assertIn(polarion_url, pol.__str__())
        self.assertIn(polarion_user, pol.__str__())
        self.assertIn(polarion_url, pol.__repr__())
        self.assertIn(polarion_user, pol.__repr__())

    @mock.patch('polarion.project.Project.__init__')
    def test_project_creation(self, mock_project):
        mock_project.return_value = None
        pol = Polarion(polarion_url, polarion_user, polarion_password)

        project = pol.getProject('Random_id')
        mock_project.assert_called_with(pol, 'Random_id')

        project = pol.getProject('other_project')
        mock_project.assert_called_with(pol, 'other_project')

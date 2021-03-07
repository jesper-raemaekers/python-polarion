import unittest
from polarion.polarion import Polarion
from polarion.project import Project
from .keys import polarion_user, polarion_password, polarion_url, polarion_project_id
from time import sleep
import mock


class TestPolarionProject(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pol = Polarion(polarion_url, polarion_user, polarion_password)
        cls.project = cls.pol.getProject(polarion_project_id)

    def setUp(self):
        pass

    def test_non_existing_project(self):
        # create project
        self.assertRaises(Exception, self.pol.getProject, 'fake_project')

    @mock.patch('polarion.workitem.Workitem.__init__')
    def test_get_workitem(self, mock_workitem):
        mock_workitem.return_value = None

        self.project.getWorkitem('FAKE-001')
        mock_workitem.assert_called_with(self.pol, self.project, 'FAKE-001')

        self.project.getWorkitem('FAKE-002')
        mock_workitem.assert_called_with(self.pol, self.project, 'FAKE-002')

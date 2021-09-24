import unittest
from polarion.polarion import Polarion
from polarion.project import Project
from keys import polarion_user, polarion_password, polarion_url, polarion_project_id
from time import sleep
import mock
from datetime import datetime


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

    def test_get_all_users(self):
        all_users = self.project.getUsers()

        self.assertGreater(len(all_users), 0)

        single_user = self.project.findUser(all_users[0].id)

        self.assertIsNotNone(single_user)

    def test_get_non_existent_user(self):
        single_user = self.project.findUser(
            'kjbhjkhbk,fbdkdjsbfgd')  # no user should be found

        self.assertIsNone(single_user)

    def test_workitem_create_and_search(self):
        new_workitem = self.project.createWorkitem('task')

        self.assertIsNotNone(new_workitem)

        search_result = self.project.searchWorkitemFullItem(new_workitem.id)

        self.assertEqual(len(search_result), 1)
        self.assertEqual(new_workitem, search_result[0])

    def test_string(self):
        self.assertIn(polarion_project_id, self.project.__str__())
        self.assertIn(polarion_project_id, self.project.__repr__())

    def test_non_existent_project(self):
        self.assertRaises(Exception, Project.__init__, self.pol, 'fake_id')

    def test_non_existent_testrun(self):
        self.assertRaises(Exception, self.project.getTestRun, 'fake_id')

    def test_get_enum(self):
        status = self.project.getEnum('status')

        self.assertGreater(len(status), 0)

    def test_testrun_search(self):
        test_runs = self.project.searchTestRuns('')

        self.assertGreater(len(test_runs), 0)

        test_run = self.project.getTestRun(test_runs[0].id)
        self.assertIsNotNone(test_run)

    def test_create_testrun(self):
        test_run = self.project.createTestRun('unit-' + datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f"), 'New unit test run', 'unittest-01')
        self.assertIsNotNone(test_run)

    @mock.patch('polarion.plan.Plan.__init__')
    def test_get_plan(self, mock_plan):
        mock_plan.return_value = None

        self.project.getPlan('FAKE-001')
        mock_plan.assert_called_with(self.pol, self.project, id='FAKE-001')

        self.project.getPlan('FAKE-002')
        mock_plan.assert_called_with(self.pol, self.project, id='FAKE-002')
        

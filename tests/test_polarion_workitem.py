import unittest
from polarion.polarion import Polarion
from polarion.project import Project
from keys import polarion_user, polarion_password, polarion_url, polarion_project_id
from time import sleep
from deepdiff import DeepDiff
import mock


class TestPolarionWorkitem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pol = Polarion(
            polarion_url, polarion_user, polarion_password)
        cls.executing_project = cls.pol.getProject(
            polarion_project_id)

        cls.checking_project = cls.pol.getProject(
            polarion_project_id)

    def setUp(self):
        pass

    def test_create_workitem(self):
        executed_workitem = self.executing_project.createWorkitem('task')
        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)

        self.assertEqual(executed_workitem, checking_workitem,
                         msg='Workitems not identical')

    def test_workitem_compare(self):
        executed_workitem = self.executing_project.createWorkitem('task')
        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)

        # status id
        new_value = 'random_val'
        executed_workitem.status.id = new_value
        self.assertNotEqual(executed_workitem, checking_workitem,
                            msg='Workitems identical, which is wrong')
        checking_workitem.status.id = new_value
        self.assertEqual(executed_workitem, checking_workitem,
                         msg='Workitems not identical')

        # title
        new_value = 'random_val'
        executed_workitem.title = new_value
        self.assertNotEqual(executed_workitem, checking_workitem,
                            msg='Workitems identical, which is wrong')
        checking_workitem.title = new_value
        self.assertEqual(executed_workitem, checking_workitem,
                         msg='Workitems not identical')

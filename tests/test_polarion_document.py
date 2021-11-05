import unittest

from polarion.polarion import Polarion
from keys import polarion_user, polarion_password, polarion_url, polarion_project_id


class TestPolarionWorkitem(unittest.TestCase):

    executing_project = None
    pol = None

    @classmethod
    def setUpClass(cls):
        cls.pol = Polarion(
            polarion_url, polarion_user, polarion_password)
        cls.executing_project = cls.pol.getProject(
            polarion_project_id)
        cls.global_workitem = cls.executing_project.createWorkitem('task')

        cls.checking_project = cls.pol.getProject(
            polarion_project_id)

    def setUp(self):
        pass

    def test_create_document(self):
        executing_document = self.executing_project.createDocument('_default', 'Test name', 'Test title', ['task'], 'relates_to')
        checking_document = self.checking_project.getDocument('_default/Test name')
        self.assertEqual(executing_document.name, checking_document.name)

        top_level_workitem = checking_document.getTopLevelWorkitem()
        self.assertEqual(top_level_workitem.name, 'Test title')

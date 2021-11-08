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
        try:
            checking_document = self.checking_project.getDocument('_default/Test name')
            if checking_document is not None:
                self.checking_project.deleteDocument(checking_document)
        except Exception:
            pass

    def test_create_document(self):
        executing_document = self.executing_project.createDocument('_default', 'Test name', 'Test title', ['task'], 'relates_to')
        checking_document = self.checking_project.getDocument('_default/Test name')
        self.assertEqual(executing_document.title, checking_document.title)

    def test_workitems_in_documents(self):
        checking_document = self.checking_project.getDocument('_default/Test name')
        heading = checking_document.add_heading('Test')
        checking_document.add_heading('Test2', heading)

        workitem = self.executing_project.createWorkitem('task')
        workitem.title = 'New document task'
        workitem.save()
        workitem.moveToDocument(checking_document, heading)

        top_level_workitem = checking_document.getTopLevelWorkitem()
        self.assertEqual(top_level_workitem.title, 'Test')

        workitem_titles = [workitem.title for workitem in checking_document.getWorkItems()]
        self.assertListEqual(workitem_titles, ['Test', 'New document task', 'Test2'])

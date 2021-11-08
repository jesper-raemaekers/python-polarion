import unittest
from datetime import datetime

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

        cls.checking_project = cls.pol.getProject(
            polarion_project_id)

        delete_documents = ['_default/Test name', '_default/Reused']
        try:
            for delete_document in delete_documents:
                checking_document = cls.checking_project.getDocument(delete_document)
                if checking_document is not None:
                    checking_document.delete()
        except Exception:
            pass

        cls.global_document = cls.executing_project.createDocument('_default', 'Test name', 'Test title', ['task'], 'relates_to')

    def test_title(self):
        checking_document = self.checking_project.getDocument('_default/Test name')
        self.assertEqual(self.global_document.title, checking_document.title)

    def test_workitems(self):
        # Add headers to it
        heading = self.global_document.addHeading('Test')
        self.global_document.addHeading('Test2', heading)

        # Create a workitem an move it into the document
        workitem = self.executing_project.createWorkitem('task')
        workitem.title = 'New document task'
        workitem.save()
        workitem.setDescription('New description')
        workitem.moveToDocument(self.global_document, heading)

        # Check that the header is the top level item
        top_level_workitem = self.global_document.getTopLevelWorkitem()
        self.assertEqual(top_level_workitem.title, 'Test')

        # Check the workitems inside the document
        workitem_titles = [workitem.title for workitem in self.global_document.getWorkitems()]
        self.assertListEqual(workitem_titles, ['Test', 'New document task', 'Test2'])

        # Reuse document
        executing_document = self.executing_project.getDocument('_default/Test name')
        reused_document = executing_document.reuse(self.executing_project.id, '_default', 'Reused', 'derived_from')

        # Now update workitem in original document
        workitem.title = 'Newer document task'
        workitem.save()
        workitem.setDescription('Newer description')

        # Make sure that the reused workitem stayed unchanged
        reused_workitems = reused_document.getWorkitems()
        self.assertEqual('New document task', reused_workitems[1].title)

        # Now update the reused document and check that the workitem's fields were updated
        reused_document.update()
        reused_workitems = reused_document.getWorkitems()
        self.assertEqual('Newer document task', reused_workitems[1].title)
        self.assertEqual('Newer description', reused_workitems[1].getDescription())

        # Now test get children
        children = self.global_document.getChildren(self.global_document.getTopLevelWorkitem())
        workitem_titles = [workitem.title for workitem in children]
        self.assertIn('Newer document task', workitem_titles)
        self.assertIn('Test2', workitem_titles)

    def test_save_document(self):
        # Change the title of a document
        self.global_document.autoSuspect = True
        self.global_document.save()

        checking_document = self.checking_project.getDocument('_default/Test name')
        self.assertTrue(checking_document.autoSuspect, 'Saving document settings failed')

    def test_get_spaces(self):
        self.assertListEqual(['_default'], self.checking_project.getDocumentSpaces())
        document_titles = [document.title for document in self.checking_project.getDocumentsInSpace('_default')]
        self.assertIn('Test title', document_titles)

    def test_add_comment(self):
        comment_text = 'New comment on ' + \
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        comment = self.global_document.addComment(comment_text)
        reply_text = 'New reply on ' + \
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.global_document.addComment(reply_text, comment)

        checking_document = self.checking_project.getDocument('_default/Test name')

        found = False
        found_reply = False
        for comment in checking_document.comments.ModuleComment:
            if comment.text.content == comment_text:
                found = True
            if comment.text.content == reply_text:
                found_reply = True
        self.assertTrue(found, 'Comment not found in checking document')
        self.assertTrue(found_reply, 'Comment reply not found in checking document')

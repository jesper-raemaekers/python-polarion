import unittest
from polarion.polarion import Polarion
from polarion.project import Project
from keys import polarion_user, polarion_password, polarion_url, polarion_project_id
from time import sleep
from datetime import datetime
import mock


class TestPolarionWorkitem(unittest.TestCase):

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

    def test_create_workitem(self):
        executed_workitem = self.executing_project.createWorkitem('task')
        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)

        self.assertEqual(executed_workitem, checking_workitem,
                         msg='Workitems not identical')

    def test_title_change(self):
        executed_workitem = self.global_workitem
        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)

        # check that new title is not in item already
        new_title = 'Unit test item ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.assertNotEqual(checking_workitem.title, new_title)

        executed_workitem.title = new_title
        executed_workitem.save()
        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)
        self.assertEqual(executed_workitem, checking_workitem,
                         msg='Workitems not identical')

    def test_description_change(self):
        executed_workitem = self.global_workitem
        new_description = 'new description on ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        #check that description is not the same as we're about to set
        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)
        self.assertNotEqual(new_description, checking_workitem.getDescription(), msg='Description cannot be the same before setting')

        #update description
        executed_workitem.setDescription(new_description)

        #check that the description now is the same
        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)
        self.assertEqual(new_description, checking_workitem.getDescription(), msg='description is not the same after setting')
        self.assertEqual(executed_workitem.getDescription(), checking_workitem.getDescription(), msg='description is not the same after setting')

    def test_add_comment(self):
        executed_workitem = self.global_workitem
        comment_title = 'New comment title on ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        comment_content = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        executed_workitem.addComment(comment_title, comment_content)

        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)
        
        found = False
        for comment in checking_workitem.comments.Comment:
            if comment.title == comment_title:
                found = True
                self.assertEqual(comment.text.content, comment_content, msg='Comment content not equal')
        self.assertTrue(found, 'Comment title not found in checking workitem')
        


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

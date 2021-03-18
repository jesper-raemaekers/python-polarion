import unittest
from polarion.polarion import Polarion
from polarion.project import Project
from keys import polarion_user, polarion_password, polarion_url, polarion_project_id
from time import sleep
from datetime import datetime
import mock
from polarion.factory import createFromUri


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
        new_description = 'new description on ' + \
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # check that description is not the same as we're about to set
        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)
        self.assertNotEqual(new_description, checking_workitem.getDescription(
        ), msg='Description cannot be the same before setting')

        # update description
        executed_workitem.setDescription(new_description)

        # check that the description now is the same
        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)
        self.assertEqual(new_description, checking_workitem.getDescription(
        ), msg='description is not the same after setting')
        self.assertEqual(executed_workitem.getDescription(), checking_workitem.getDescription(
        ), msg='description is not the same after setting')

    def test_add_comment(self):
        executed_workitem = self.global_workitem
        comment_title = 'New comment title on ' + \
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        comment_content = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        executed_workitem.addComment(comment_title, comment_content)

        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)

        found = False
        for comment in checking_workitem.comments.Comment:
            if comment.title == comment_title:
                found = True
                self.assertEqual(
                    comment.text.content, comment_content, msg='Comment content not equal')
        self.assertTrue(found, 'Comment title not found in checking workitem')

    def test_assignee(self):
        self.assertEqual(len(self.global_workitem.getAssignedUsers(
        )), 0, msg='Testing workitem should have no assigned users')

        # find and add user
        user = self.executing_project.getUsers()[0]
        self.global_workitem.addAssignee(user)

        checking_workitem = self.checking_project.getWorkitem(
            self.global_workitem.id)

        executing_users = self.global_workitem.getAssignedUsers()
        checking_users = checking_workitem.getAssignedUsers()

        self.assertEqual(len(executing_users), 1,
                         msg='executing workitem should have 1 assigned users')
        self.assertEqual(len(checking_users),
                         1, msg='checking workitem should have 1 assigned users')

        # check if the users are the same
        self.assertEqual(executing_users[0], checking_users[0])

        # now remove the user
        self.global_workitem.removeAssignee(executing_users[0])

        checking_workitem = self.checking_project.getWorkitem(
            self.global_workitem.id)

        executing_users = self.global_workitem.getAssignedUsers()
        checking_users = checking_workitem.getAssignedUsers()

        self.assertEqual(len(executing_users), 0,
                         msg='executing workitem should have 0 assigned users')
        self.assertEqual(len(checking_users),
                         0, msg='checking workitem should have 0 assigned users')

    def test_replace_assignee(self):
        self.assertGreater(len(self.executing_project.getUsers(
        )), 1, msg='Project does not have more than 1 user in project')

        self.assertEqual(len(self.global_workitem.getAssignedUsers(
        )), 0, msg='Testing workitem should have no assigned users')

        # find and add user
        user = self.executing_project.getUsers()[0]

        self.global_workitem.addAssignee(user)

        checking_workitem = self.checking_project.getWorkitem(
            self.global_workitem.id)

        executing_users = self.global_workitem.getAssignedUsers()
        checking_users = checking_workitem.getAssignedUsers()

        self.assertEqual(len(executing_users), 1,
                         msg='executing workitem should have 1 assigned users')
        self.assertEqual(len(checking_users),
                         1, msg='checking workitem should have 1 assigned users')

        # check if the users are the same
        self.assertEqual(executing_users[0], checking_users[0])

        # now replace the user
        user = self.executing_project.getUsers()[1]

        self.global_workitem.addAssignee(user, True)

        checking_workitem = self.checking_project.getWorkitem(
            self.global_workitem.id)

        executing_users = self.global_workitem.getAssignedUsers()
        checking_users = checking_workitem.getAssignedUsers()

        self.assertEqual(len(executing_users), 1,
                         msg='executing workitem should have 0 assigned users')
        self.assertEqual(len(checking_users),
                         1, msg='checking workitem should have 0 assigned users')

        self.assertEqual(executing_users[0], checking_users[0])

    @mock.patch('polarion.project.Project.getEnum')
    def test_get_enum(self, mock_project):
        expected_return = ['a', 'b', 'c']
        mock_project.return_value = expected_return
        actual_return = self.global_workitem.getStatusEnum()
        mock_project.assert_called_with('task-status')
        self.assertEqual(expected_return, actual_return,
                         msg='Return value not equal to mock')

        actual_return = self.global_workitem.getResolutionEnum()
        mock_project.assert_called_with('task-resolution')
        self.assertEqual(expected_return, actual_return,
                         msg='Return value not equal to mock')

        actual_return = self.global_workitem.getSeverityEnum()
        mock_project.assert_called_with('task-severity')
        self.assertEqual(expected_return, actual_return,
                         msg='Return value not equal to mock')

        expected_return = []
        mock_project.side_effect = Exception('Dummy exception')
        actual_return = self.global_workitem.getStatusEnum()
        mock_project.assert_called_with('task-status')
        self.assertEqual(expected_return, actual_return,
                         msg='Return value not empty array')

        actual_return = self.global_workitem.getResolutionEnum()
        mock_project.assert_called_with('task-resolution')
        self.assertEqual(expected_return, actual_return,
                         msg='Return value not empty array')

        actual_return = self.global_workitem.getSeverityEnum()
        mock_project.assert_called_with('task-severity')
        self.assertEqual(expected_return, actual_return,
                         msg='Return value not empty array')

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

    def test_workitem_creator(self):
        new_workitem = createFromUri(self.pol, self.executing_project, self.global_workitem.uri)
        
        self.assertEqual(self.global_workitem, new_workitem,
                         msg='Workitems not identical')

    def test_workitem_author_creator(self):
        author = createFromUri(self.pol, self.executing_project, self.global_workitem.author.uri)
        
        self.assertEqual(self.global_workitem.author.id, author.id,
                         msg='Authors not identical')
import unittest
from unittest.mock import MagicMock
from polarion.polarion import Polarion
from polarion.project import Project
from keys import polarion_user, polarion_password, polarion_url, polarion_project_id
from time import sleep
from datetime import datetime
import mock
from polarion.factory import createFromUri
from filecmp import cmp
from shutil import copyfile


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

    def test_add_comment_not_available(self):
        # create a local polarion service as we'll destroy the global one
        polarion = Polarion(
            polarion_url, polarion_user, polarion_password)        

        executing_project = polarion.getProject(
            polarion_project_id)

        executing_workitem = executing_project.getWorkitem(self.global_workitem.id)

        # replace the getService with someting that will not return anything with content.
        polarion.getService = MagicMock(return_value={})

        with self.assertRaises(Exception):
            executing_workitem.addComment('', 'A comment that will fail')

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

    def test_attachment(self):
        self.assertFalse(self.global_workitem.hasAttachment(), msg='Workitem already has attachments')
        src_1 = 'tests/test_image_1.png'
        src_2 = 'tests/test_image_2.png'
        dst = 'tests/test_image.png'
        download = 'tests/test_image_result.png'
        copyfile(src_1, dst)

        self.global_workitem.addAttachment(dst, 'Test image 1')

        self.assertTrue(self.global_workitem.hasAttachment(), msg='Workitem has no attachments')

        attachment_id = self.global_workitem.attachments.Attachment[0].id

        self.global_workitem.saveAttachmentAsFile(attachment_id, download)

        self.assertTrue(cmp(src_1, download), 'File downloaded from polarion not the same')
        
        copyfile(src_2, dst)

        self.global_workitem.updateAttachment(attachment_id, dst, 'Test image 1')

        self.global_workitem.saveAttachmentAsFile(attachment_id, download)

        self.assertTrue(cmp(src_2, download), 'File downloaded from polarion not the same')
        self.assertFalse(cmp(src_1, download), 'File downloaded from polarion is the same as the old file')

        self.global_workitem.deleteAttachment(attachment_id)

        self.assertFalse(self.global_workitem.hasAttachment(), msg='Workitem has attachments, but should not')
    
    def test_set_status(self):
        executed_workitem = self.executing_project.createWorkitem('task')

        new_value = 'random_val'
        executed_workitem.setStatus(new_value)
        self.assertNotEqual(executed_workitem.status.id, new_value, msg="Workitem should not have updated to illegal value")

        new_value = executed_workitem.getAvailableStatus()[-1]
        executed_workitem.setStatus(new_value)
        self.assertEqual(executed_workitem.status.id, new_value, msg="Workitem should have updated to new value")

    def test_add_link(self):
        executed_workitem_1 = self.executing_project.createWorkitem('task')
        executed_workitem_2 = self.executing_project.createWorkitem('task')        

        self.assertIsNone(executed_workitem_1.linkedWorkItems, msg='Workitem already has a link')
        self.assertIsNone(executed_workitem_2.linkedWorkItems, msg='Workitem already has a link')

        executed_workitem_1.addLinkedItem(executed_workitem_2, 'relates_to')

        self.assertIsNotNone(executed_workitem_1.linkedWorkItems, msg='Workitem already has no link')

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id)
        checking_workitem_2 = self.checking_project.getWorkitem(executed_workitem_2.id)

        self.assertEqual('relates_to', checking_workitem_1.linkedWorkItems.LinkedWorkItem[0].role.id)
        self.assertEqual('relates_to', checking_workitem_2.linkedWorkItemsDerived.LinkedWorkItem[0].role.id)
        self.assertEqual(checking_workitem_2.uri, checking_workitem_1.linkedWorkItems.LinkedWorkItem[0].workItemURI)
        self.assertEqual(checking_workitem_1.uri, checking_workitem_2.linkedWorkItemsDerived.LinkedWorkItem[0].workItemURI)


    def test_remove_link(self):
        executed_workitem_1 = self.executing_project.createWorkitem('task')
        executed_workitem_2 = self.executing_project.createWorkitem('task')      
        
        # test 1: create link and remove with role
        executed_workitem_1.addLinkedItem(executed_workitem_2, 'relates_to') 

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertIsNotNone(executed_workitem_1.linkedWorkItems, msg='Workitem already has no link')
        self.assertIsNotNone(checking_workitem_1.linkedWorkItems, msg='Workitem already has no link')

        executed_workitem_1.removeLinkedItem(executed_workitem_2, 'relates_to')

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertIsNone(executed_workitem_1.linkedWorkItems, msg='Workitem already has link remaining')
        self.assertIsNone(checking_workitem_1.linkedWorkItems, msg='Workitem already has link remaining')

        # test 2: create link and remove without role
        executed_workitem_1.addLinkedItem(executed_workitem_2, 'relates_to') 

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertIsNotNone(executed_workitem_1.linkedWorkItems, msg='Workitem already has no link')
        self.assertIsNotNone(checking_workitem_1.linkedWorkItems, msg='Workitem already has no link')

        executed_workitem_1.removeLinkedItem(executed_workitem_2)

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertIsNone(executed_workitem_1.linkedWorkItems, msg='Workitem already has link remaining')
        self.assertIsNone(checking_workitem_1.linkedWorkItems, msg='Workitem already has link remaining')

        # test 3: create link and remove from derived item        

        executed_workitem_1.addLinkedItem(executed_workitem_2, 'relates_to') 

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertIsNotNone(executed_workitem_1.linkedWorkItems, msg='Workitem already has no link')
        self.assertIsNotNone(checking_workitem_1.linkedWorkItems, msg='Workitem already has no link')

        executed_workitem_2.removeLinkedItem(executed_workitem_1)

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertIsNone(executed_workitem_1.linkedWorkItems, msg='Workitem already has link remaining')
        self.assertIsNone(checking_workitem_1.linkedWorkItems, msg='Workitem already has link remaining')

    def test_custom_field(self):
        executed_workitem_1 = self.executing_project.createWorkitem('task')

        self.assertIsNone(executed_workitem_1.customFields, msg='Workitem already has a custom field')

        executed_workitem_1.setCustomField(key='int_field', value=12)

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertIsNotNone(executed_workitem_1.customFields, msg='Workitem already does not have a custom field')
        self.assertEqual(12, executed_workitem_1.customFields.Custom[0].value, msg='value not the same as set')
        self.assertIsNotNone(checking_workitem_1.customFields, msg='Workitem already does not have a custom field')
        self.assertEqual(12, checking_workitem_1.customFields.Custom[0].value, msg='value not the same as set')

        executed_workitem_1.setCustomField(key='int_field', value=24)

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertEqual(24, executed_workitem_1.customFields.Custom[0].value, msg='value not the same as set')
        self.assertEqual(24, checking_workitem_1.customFields.Custom[0].value, msg='value not the same as set')

        executed_workitem_1.setCustomField(key='string_field', value='12')

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 
        self.assertEqual('12', executed_workitem_1.customFields.Custom[0].value, msg='value not the same as set')
        self.assertEqual('12', checking_workitem_1.customFields.Custom[0].value, msg='value not the same as set')

        self.assertRaises(Exception, executed_workitem_1.setCustomField, 'random_invalid_key', 0)

    def test_approvee(self):
        executed_workitem_1 = self.executing_project.createWorkitem('task')
        all_users = self.executing_project.getUsers()
        testing_user_1 = all_users[0]
        testing_user_2 = all_users[1]

        executed_workitem_1.addApprovee(testing_user_1)

        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertEqual(executed_workitem_1.approvals.Approval[0].user.id, testing_user_1.id, msg='Approving user not equal to assign user')
        self.assertEqual(checking_workitem_1.approvals.Approval[0].user.id, testing_user_1.id, msg='Approving user not equal to assign user')

        executed_workitem_1.removeApprovee(testing_user_1)
        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertIsNone(executed_workitem_1.approvals, msg='approvee not removed')
        self.assertIsNone(checking_workitem_1.approvals, msg='approvee not removed')

        executed_workitem_1.addApprovee(testing_user_1)
        executed_workitem_1.addApprovee(testing_user_2, remove_others=True)
        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id)
        self.assertEqual(executed_workitem_1.approvals.Approval[0].user.id, testing_user_2.id, msg='Approving user not equal to assign user')
        self.assertEqual(checking_workitem_1.approvals.Approval[0].user.id, testing_user_2.id, msg='Approving user not equal to assign user')

    def test_resolution(self):
        executed_workitem_1 = self.executing_project.createWorkitem('task')

        resolutions = executed_workitem_1.getResolutionEnum()
        
        executed_workitem_1.setResolution('done')
        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertEqual(executed_workitem_1.resolution.id, 'done', msg='Resolution not as set')
        self.assertEqual(checking_workitem_1.resolution.id, 'done', msg='Resolution not as set')

        executed_workitem_1.setResolution('incomplete')
        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id) 

        self.assertEqual(executed_workitem_1.resolution.id, 'incomplete', msg='Resolution not as set')
        self.assertEqual(checking_workitem_1.resolution.id, 'incomplete', msg='Resolution not as set')



        

        



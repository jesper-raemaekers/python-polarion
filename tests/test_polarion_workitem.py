import unittest
from unittest.mock import MagicMock
from polarion.polarion import Polarion
from polarion.project import Project
from keys import polarion_user, polarion_password, polarion_url, polarion_project_id
from time import sleep
from datetime import datetime
from unittest import mock
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

        # Check that fields can be supplied with the call
        executed_workitem = self.executing_project.createWorkitem('task', new_workitem_fields={'title': 'Test title!'})
        checking_workitem = self.checking_project.getWorkitem(
            executed_workitem.id)

        self.assertEqual(executed_workitem, checking_workitem,
                         msg='Workitems not identical when created with supplied fields')

        # Check that fields are checks for validity
        with self.assertRaises(Exception):
            executed_workitem = self.executing_project.createWorkitem('task', new_workitem_fields={'wrong-field': 'what happens?'})

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
        src_1 = 'test_image_1.png'
        src_2 = 'test_image_2.png'
        dst = 'test_image.png'
        download = 'test_image_result.png'
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
        self.assertEqual('12', executed_workitem_1.customFields.Custom[1].value, msg='value not the same as set')
        self.assertEqual('12', checking_workitem_1.customFields.Custom[1].value, msg='value not the same as set')

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

    def test_hyperlink(self):
        # setup
        url = 'https://github.com/jesper-raemaekers/python-polarion'
        executed_workitem_1 = self.executing_project.createWorkitem('task')

        # check if there is no hyperlink before starting
        self.assertIsNone(executed_workitem_1.hyperlinks, msg='Workitem already has a hyperlink')

        # add a hyperlink and load checking workitem
        executed_workitem_1.addHyperlink(url, executed_workitem_1.HyperlinkRoles.EXTERNAL_REF)
        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id)

        # checks
        self.assertIsNotNone(executed_workitem_1.hyperlinks, msg='Workitem already has no hyperlink')
        self.assertEqual('external reference', executed_workitem_1.hyperlinks.Hyperlink[0].role.id)
        self.assertEqual('external reference', checking_workitem_1.hyperlinks.Hyperlink[0].role.id)
        self.assertEqual(url, executed_workitem_1.hyperlinks.Hyperlink[0].uri)
        self.assertEqual(url, checking_workitem_1.hyperlinks.Hyperlink[0].uri)

        # remove hyperlink and load checking workitem
        executed_workitem_1.removeHyperlink(url)
        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id)

        # checks
        self.assertIsNone(executed_workitem_1.hyperlinks, msg='Workitem still has a hyperlink')
        self.assertIsNone(checking_workitem_1.hyperlinks, msg='Workitem still has a hyperlink')

        # add a hyperlink and load checking workitem
        executed_workitem_1.addHyperlink(url, executed_workitem_1.HyperlinkRoles.INTERNAL_REF)
        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id)

        # checks
        self.assertIsNotNone(executed_workitem_1.hyperlinks, msg='Workitem already has no hyperlink')
        self.assertEqual('internal reference', executed_workitem_1.hyperlinks.Hyperlink[0].role.id)
        self.assertEqual('internal reference', checking_workitem_1.hyperlinks.Hyperlink[0].role.id)
        self.assertEqual(url, executed_workitem_1.hyperlinks.Hyperlink[0].uri)
        self.assertEqual(url, checking_workitem_1.hyperlinks.Hyperlink[0].uri)

        # remove hyperlink and load checking workitem
        executed_workitem_1.removeHyperlink(url)
        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id)

        # checks
        self.assertIsNone(executed_workitem_1.hyperlinks, msg='Workitem still has a hyperlink')
        self.assertIsNone(checking_workitem_1.hyperlinks, msg='Workitem still has a hyperlink')

        # add a hyperlink and load checking workitem
        executed_workitem_1.addHyperlink(url, 'internal reference')
        checking_workitem_1 = self.checking_project.getWorkitem(executed_workitem_1.id)

        # checks
        self.assertIsNotNone(executed_workitem_1.hyperlinks, msg='Workitem already has no hyperlink')
        self.assertEqual('internal reference', executed_workitem_1.hyperlinks.Hyperlink[0].role.id)
        self.assertEqual('internal reference', checking_workitem_1.hyperlinks.Hyperlink[0].role.id)
        self.assertEqual(url, executed_workitem_1.hyperlinks.Hyperlink[0].uri)
        self.assertEqual(url, checking_workitem_1.hyperlinks.Hyperlink[0].uri)


    def test_testcase_column_names(self):
        executed_workitem_1 = self.executing_project.createWorkitem('testcase')
        executed_workitem_2 = self.executing_project.createWorkitem('task')

        # get column names
        column_names = executed_workitem_1.getTestStepHeader()
        # check names
        self.assertIn('Step', column_names, msg='Column name Step not found')
        self.assertIn('Step Description', column_names, msg='Column name Step Description not found')
        self.assertIn('Expected Result', column_names, msg='Column name Expected Result not found')
        self.assertIn('step', executed_workitem_1.getTestStepHeaderID())
        self.assertIn('description', executed_workitem_1.getTestStepHeaderID())
        self.assertIn('expectedResult', executed_workitem_1.getTestStepHeaderID())

        # check for exception when called on a non test case workitem
        with self.assertRaises(Exception) as ex:
            column_names = executed_workitem_2.getTestStepHeader()
        self.assertIn('Work item does not have test step custom field', str(ex.exception))

        with self.assertRaises(Exception) as ex:
            executed_workitem_2.getTestStepHeaderID()
        self.assertIn('Work item does not have test step custom field',
                      str(ex.exception))

        # do it again but now with existing test case
        executed_workitem_3 = self.executing_project.getWorkitem(executed_workitem_1.id)

        # get column names
        column_names = executed_workitem_3.getTestStepHeader()
        # check names
        self.assertIn('Step', column_names, msg='Column name Step not found')
        self.assertIn('Step Description', column_names, msg='Column name Step Description not found')
        self.assertIn('Expected Result', column_names, msg='Column name Expected Result not found')


    def test_testcase_add_remove_steps(self):
        executed_workitem_1 = self.executing_project.createWorkitem('testcase')
        executed_workitem_2 = self.executing_project.createWorkitem('task')

        # check for exception when called with too many argument
        with self.assertRaises(Exception) as ex:
            executed_workitem_1.addTestStep('','','','')
        self.assertIn('Incorrect number of argument. Test step requires 3 arguments.', str(ex.exception))

        # check for exception when called with too little argument
        with self.assertRaises(Exception) as ex:
            executed_workitem_1.addTestStep('', '')
        self.assertIn('Incorrect number of argument. Test step requires 3 arguments.', str(ex.exception))

        # check for exception when called on a non test case workitem
        with self.assertRaises(Exception) as ex:
            executed_workitem_2.addTestStep('','','')
        self.assertIn('Cannot add test steps to work item that does not have the custom field', str(ex.exception))

        # check length of returned test steps
        self.assertEqual(0, len(executed_workitem_1.getTestSteps()),
                         msg='Length of test steps is not 0 when creating a new item')

        # add some test steps
        for i in range(3):
            executed_workitem_1.addTestStep(f'{i}', f'Test step {i}', '')

        # check length again
        self.assertEqual(3, len(executed_workitem_1.getTestSteps()),
                         msg='Length of test steps is not 3')

        # remove middle test step
        executed_workitem_1.removeTestStep(1)

        # check length to be 1 less
        self.assertEqual(2, len(executed_workitem_1.getTestSteps()),
                         msg='Length of test steps is not 2')

        self.assertEqual('0', executed_workitem_1.getTestSteps()[0]['step'], msg='Test step 0 was not found anymore')
        self.assertEqual('2', executed_workitem_1.getTestSteps()[1]['step'], msg='Test step 2 was not found anymore')

        # try removing test step from task
        with self.assertRaises(Exception) as ex:
            executed_workitem_2.removeTestStep(0)
        self.assertIn('Cannot remove test steps to work item that does not have the custom field', str(ex.exception))

        # try removing a test step out of range
        with self.assertRaises(Exception) as ex:
            executed_workitem_1.removeTestStep(99)
        self.assertIn('Index should be in range of test step length of', str(ex.exception))


    def test_testcase_update_steps(self):
        executed_workitem_1 = self.executing_project.createWorkitem('testcase')
        executed_workitem_2 = self.executing_project.createWorkitem('task')

        # add some test steps
        for i in range(3):
            executed_workitem_1.addTestStep(f'{i}', f'Test step {i}', f'nothing here {i}')

        # check that all values
        for i in range(3):
            self.assertEqual(f'{i}', executed_workitem_1.getTestSteps()[i]['step'], msg='Value in first column changes since creation')
            self.assertEqual(f'Test step {i}', executed_workitem_1.getTestSteps()[i]['description'], msg='Value in second column changes since creation')
            self.assertEqual(f'nothing here {i}', executed_workitem_1.getTestSteps()[i]['expectedResult'], msg='Value in third column changes since creation')

        # check for exception when called with too many argument
        with self.assertRaises(Exception) as ex:
            executed_workitem_1.updateTestStep(0, '','','','')
        self.assertIn('Incorrect number of argument. Test step requires 3 arguments.', str(ex.exception))

        # check for exception when called with too little argument
        with self.assertRaises(Exception) as ex:
            executed_workitem_1.updateTestStep(0, '', '')
        self.assertIn('Incorrect number of argument. Test step requires 3 arguments.', str(ex.exception))

         # check for exception when index is not provided
        with self.assertRaises(Exception) as ex:
            executed_workitem_1.updateTestStep('', '', '')
        self.assertIn('First argument of updateTestStep must be an integer.', str(ex.exception))

        # check for exception when called on a non test case workitem
        with self.assertRaises(Exception) as ex:
            executed_workitem_2.updateTestStep(0, '','','')
        self.assertIn('Cannot update test steps to work item that does not have the custom field', str(ex.exception))

        # try removing a test step out of range
        with self.assertRaises(Exception) as ex:
            executed_workitem_1.updateTestStep(99, '', '', '')
        self.assertIn('Index should be in range of test step length of', str(ex.exception))

        # change all steps
        for i in range(3):
            executed_workitem_1.updateTestStep(i, f'{i + 10}', f'new {i + 20}', f'last {i + 20}')

        # check again
        for i in range(3):
            self.assertEqual(f'{10 + i}', executed_workitem_1.getTestSteps()[i]['step'], msg='Value in first column did not change')
            self.assertEqual(f'new {i + 20}', executed_workitem_1.getTestSteps()[i]['description'], msg='Value in second column did not change')
            self.assertEqual(f'last {i + 20}', executed_workitem_1.getTestSteps()[i]['expectedResult'], msg='Value in third column did not change')

    def test_get_linked_items(self):
        executed_workitem_1 = self.executing_project.createWorkitem('task')
        executed_workitem_2 = self.executing_project.createWorkitem('task')

        # check empty linked items
        self.assertEqual(0, len(executed_workitem_1.getLinkedItemWithRoles()), msg='Linked workitem not 0 in length')
        self.assertEqual(0, len(executed_workitem_1.getLinkedItem()), msg='Linked workitem not 0 in length')

        # add link
        executed_workitem_1.addLinkedItem(executed_workitem_2, 'follow_up')

        # check non empty linked items
        self.assertEqual(1, len(executed_workitem_1.getLinkedItemWithRoles()), msg='Linked workitem not 1 in length')
        self.assertEqual(1, len(executed_workitem_1.getLinkedItem()), msg='Linked workitem not 1 in length')
        self.assertEqual(1, len(executed_workitem_2.getLinkedItemWithRoles()), msg='Linked workitem not 1 in length')
        self.assertEqual(1, len(executed_workitem_2.getLinkedItem()), msg='Linked workitem not 1 in length')

        self.assertEqual(executed_workitem_2, executed_workitem_1.getLinkedItemWithRoles()[0][1],
                         msg='Check workitem')
        self.assertEqual('follow_up', executed_workitem_1.getLinkedItemWithRoles()[0][0],
                         msg='Check link type')
        self.assertEqual(executed_workitem_2, executed_workitem_1.getLinkedItem()[0],
                         msg='Check workitem')

        self.assertEqual(executed_workitem_1, executed_workitem_2.getLinkedItemWithRoles()[0][1],
                         msg='Check workitem')
        self.assertEqual('follow_up', executed_workitem_2.getLinkedItemWithRoles()[0][0],
                         msg='Check link type')
        self.assertEqual(executed_workitem_1, executed_workitem_2.getLinkedItem()[0],
                         msg='Check workitem')
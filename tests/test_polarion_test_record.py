import unittest
from polarion.polarion import Polarion
from polarion.project import Project
from polarion.record import Record
from keys import polarion_user, polarion_password, polarion_url, polarion_project_id
from time import sleep
from datetime import datetime
import mock
from polarion.factory import createFromUri
from filecmp import cmp
from shutil import copyfile


class TestPolarionTestRecord(unittest.TestCase):
    # this test requires a test run template to exist.
    # this test run template must have 3 test cases
    # all test cases must have minimum 2 steps

    @classmethod
    def setUpClass(cls):
        cls.pol = Polarion(
            polarion_url, polarion_user, polarion_password)
        cls.executing_project = cls.pol.getProject(
            polarion_project_id)
        cls.testrun_id = 'unit-' + datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f")
        cls.executing_test_run = cls.executing_project.createTestRun(cls.testrun_id, 'New unit test run', 'unittest-01')
        cls.executing_test_record = cls.executing_test_run.records[0]

        cls.checking_project = cls.pol.getProject(
            polarion_project_id)

    def setUp(self):
        pass

    def test_str_repr(self):
        self.assertIsNone(self.executing_test_run.records[2].getExecutingUser(), 'Executing use not None')

        self.assertIn(self.testrun_id, self.executing_test_run.records[2].__str__())
        self.assertIn(self.testrun_id, self.executing_test_run.records[2].__repr__())
        self.assertIn(str(Record.ResultType.No), self.executing_test_run.records[2].__str__())
        self.assertIn(str(Record.ResultType.No), self.executing_test_run.records[2].__repr__())

        self.executing_test_run.records[2].setResult(Record.ResultType.PASSED)

        self.assertIn(str(Record.ResultType.PASSED), self.executing_test_run.records[2].__str__())
        self.assertIn(str(Record.ResultType.PASSED), self.executing_test_run.records[2].__repr__())

        self.assertIn(self.pol.user, self.executing_test_run.records[2].getExecutingUser().id)



    def test_record_status(self):
        executing_test_record = self.executing_test_run.records[1]

        self.assertEqual(executing_test_record.result, None, msg='Result already set')
        self.assertEqual(executing_test_record.getResult(), Record.ResultType.No, msg='Result already set')

        passed_comment = 'This is the comment when it passed!'
        executing_test_record.setResult(Record.ResultType.PASSED, passed_comment)

        checking_test_record = self.checking_project.getTestRun(self.executing_test_run.id).records[1]

        self.assertEqual(executing_test_record.result.id, 'passed', msg='Result not set to passed')
        self.assertEqual(executing_test_record.getResult(), Record.ResultType.PASSED, msg='Result not set to passed')
        self.assertEqual(executing_test_record.getComment(), passed_comment, msg='Comment not the same')

        self.assertEqual(checking_test_record.result.id, 'passed', msg='Result not set to passed')
        self.assertEqual(checking_test_record.getResult(), Record.ResultType.PASSED, msg='Result not set to passed')
        self.assertEqual(checking_test_record.getComment(), passed_comment, msg='Comment not the same')

        new_passed_comment = 'a new comment'
        executing_test_record.setResult(Record.ResultType.BLOCKED, new_passed_comment)
        checking_test_record = self.checking_project.getTestRun(self.executing_test_run.id).records[1]

        self.assertEqual(executing_test_record.result.id, 'blocked', msg='Result not set to passed')
        self.assertEqual(executing_test_record.getResult(), Record.ResultType.BLOCKED, msg='Result not set to passed')
        self.assertIn(new_passed_comment, executing_test_record.getComment(), msg='Comment not added ')

        self.assertEqual(checking_test_record.result.id, 'blocked', msg='Result not set to passed')
        self.assertEqual(checking_test_record.getResult(), Record.ResultType.BLOCKED, msg='Result not set to passed')
        self.assertIn(new_passed_comment, checking_test_record.getComment(), msg='Comment not added')

    def test_attachment_test_step(self):
        for step_index in range(1):
            self.executing_test_record.setTestStepResult(step_index, Record.ResultType.PASSED, 'See attachment')

            self.assertFalse(self.executing_test_record.testStepHasAttachment(step_index), msg='Test step already has attachments')

            src_1 = 'test_image_1.png'
            src_2 = 'test_image_2.png'
            download = 'test_image_result.png'

            self.executing_test_record.addAttachmentToTestStep(step_index, src_1, 'Test image 1')

            self.assertTrue(self.executing_test_record.testStepHasAttachment(step_index), msg='Test step does not have attachments')
            self.assertFalse(self.executing_test_record.testStepHasAttachment(step_index + 1), msg='Test step already has attachments')

            attachment_file1 = self.executing_test_record.testStepResults.TestStepResult[step_index].attachments.TestRunAttachment[0].fileName

            self.executing_test_record.saveAttachmentFromTestStepAsFile(step_index, attachment_file1, download)

            self.assertTrue(cmp(src_1, download), 'File downloaded from polarion not the same')
            
            self.executing_test_record.addAttachmentToTestStep(step_index, src_2, 'Test image 2')

            attachment_file2 = self.executing_test_record.testStepResults.TestStepResult[step_index].attachments.TestRunAttachment[1].fileName

            self.executing_test_record.saveAttachmentFromTestStepAsFile(step_index, attachment_file2, download)

            self.assertTrue(cmp(src_2, download), 'File downloaded from polarion not the same')
            self.assertFalse(cmp(src_1, download), 'File downloaded from polarion is the same as the old file')

            self.executing_test_record.deleteAttachmentFromTestStep(step_index, attachment_file1)
            self.executing_test_record.deleteAttachmentFromTestStep(step_index, attachment_file2)

            self.assertFalse(self.executing_test_record.testStepHasAttachment(step_index), msg='Test step still has attachments')

    def test_attachment(self):
        self.executing_test_record.setResult(Record.ResultType.BLOCKED, 'See attachment')

        self.assertFalse(self.executing_test_record.hasAttachment(), msg='Record already has attachments')
        src_1 = 'test_image_1.png'
        src_2 = 'test_image_2.png'
        download = 'test_image_result.png'


        self.executing_test_record.addAttachment(src_1, 'Test image 1')

        self.assertTrue(self.executing_test_record.hasAttachment(), msg='Record has no attachments')

        attachment_file1 = self.executing_test_record.attachments.TestRunAttachment[0].fileName        

        self.executing_test_record.saveAttachmentAsFile(attachment_file1, download)

        self.assertTrue(cmp(src_1, download), 'File downloaded from polarion not the same')
        
        self.executing_test_record.addAttachment(src_2, 'Test image 2')

        attachment_file2 = self.executing_test_record.attachments.TestRunAttachment[1].fileName    

        self.executing_test_record.saveAttachmentAsFile(attachment_file2, download)

        self.assertTrue(cmp(src_2, download), 'File downloaded from polarion not the same')
        self.assertFalse(cmp(src_1, download), 'File downloaded from polarion is the same as the old file')

        self.executing_test_record.deleteAttachment(attachment_file1)
        self.executing_test_record.deleteAttachment(attachment_file2)

        self.assertFalse(self.executing_test_record.hasAttachment(), msg='Record has attachments, but should not')

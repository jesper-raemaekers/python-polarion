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

    @classmethod
    def setUpClass(cls):
        cls.pol = Polarion(
            polarion_url, polarion_user, polarion_password)
        cls.executing_project = cls.pol.getProject(
            polarion_project_id)
            
        cls.executing_test_run = cls.executing_project.createTestRun('unit-' + datetime.now().strftime("%d-%m-%Y-%H-%M-%S"), 'New unit test run', 'unittest-01')
        cls.executing_test_record = cls.executing_test_run.records[0]

        cls.checking_project = cls.pol.getProject(
            polarion_project_id)

    def setUp(self):
        pass

    def test_attachment(self):
        # self.executing_test_record.setTestStepResult(0, Record.ResultType.PASSED, 'See attachment')
        self.executing_test_record.setResult(Record.ResultType.BLOCKED, 'See attachment')

        checking_testrun = self.checking_project.getTestRun(self.executing_test_run.id)
        checking_test_record = checking_testrun.records[0]

        self.assertFalse(self.executing_test_record.hasAttachment(), msg='Workitem already has attachments')
        src_1 = 'tests/test_image_1.png'
        src_2 = 'tests/test_image_2.png'
        download = 'tests/test_image_result.png'


        self.executing_test_record.addAttachment(src_1, 'Test image 1')

        self.assertTrue(self.executing_test_record.hasAttachment(), msg='Workitem has no attachments')

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

        self.assertFalse(self.executing_test_record.hasAttachment(), msg='Workitem has attachments, but should not')

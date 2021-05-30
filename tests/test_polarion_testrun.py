import unittest
from polarion.polarion import Polarion
from polarion.project import Project
from keys import polarion_user, polarion_password, polarion_url, polarion_project_id
from time import sleep
from datetime import datetime
import mock
from polarion.factory import createFromUri
from filecmp import cmp
from shutil import copyfile


class TestPolarionTestrun(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pol = Polarion(
            polarion_url, polarion_user, polarion_password)
        cls.executing_project = cls.pol.getProject(
            polarion_project_id)
            
        cls.executing_test_run = cls.executing_project.createTestRun('unit-' + datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f"), 'New unit test run', 'unittest-01')

        cls.checking_project = cls.pol.getProject(
            polarion_project_id)

    def setUp(self):
        pass

    def test_record_list(self):
        #build list of recods
        checking_testrun = self.checking_project.getTestRun(self.executing_test_run.id)
        list_record = []
        for r in checking_testrun.records:
            list_record.append(r.getTestCaseName())

            self.assertTrue(self.executing_test_run.hasTestCase(r.getTestCaseName()), msg='Test run does not have test case it should have')
            executing_record = self.executing_test_run.getTestCase(r.getTestCaseName())
            checking_record = checking_testrun.getTestCase(r.getTestCaseName())
            
            self.assertEqual(executing_record.getTestCaseName(), checking_record.getTestCaseName(), msg='Records did not match')
        
        self.assertFalse(self.executing_test_run.hasTestCase(list_record[0] + 'invalid'), msg='Invalid test case was available')
        self.assertIsNone(self.executing_test_run.getTestCase(list_record[0] + 'invalid'), msg='Invalid test case was returned')


    def test_run_status(self):
        self.assertEqual(self.executing_test_run.status.id, 'open', msg='Status is not open')

        self.executing_test_run.status.id = 'verifiedPassed'
        self.executing_test_run.save()

        self.assertEqual(self.executing_test_run.status.id, 'verifiedPassed', msg='Status is not verifiedPassed')

        checking_testrun = self.checking_project.getTestRun(self.executing_test_run.id)

        self.assertEqual(checking_testrun.status.id, 'verifiedPassed', msg='Status is not verifiedPassed')


  
    def test_attachment(self):
        self.assertFalse(self.executing_test_run.hasAttachment(), msg='Workitem already has attachments')
        src_1 = 'tests/test_image_1.png'
        src_2 = 'tests/test_image_2.png'
        dst = 'tests/test_image.png'
        download = 'tests/test_image_result.png'
        copyfile(src_1, dst)

        self.executing_test_run.addAttachment(dst, 'Test image 1')

        self.assertTrue(self.executing_test_run.hasAttachment(), msg='Workitem has no attachments')

        attachment_file = self.executing_test_run.attachments.TestRunAttachment[0].fileName        

        self.executing_test_run.saveAttachmentAsFile(attachment_file, download)

        self.assertTrue(cmp(src_1, download), 'File downloaded from polarion not the same')
        
        copyfile(src_2, dst)

        self.executing_test_run.updateAttachment(dst, 'Test image 1')

        self.executing_test_run.saveAttachmentAsFile(attachment_file, download)

        self.assertTrue(cmp(src_2, download), 'File downloaded from polarion not the same')
        self.assertFalse(cmp(src_1, download), 'File downloaded from polarion is the same as the old file')

        self.executing_test_run.deleteAttachment(attachment_file)

        self.assertFalse(self.executing_test_run.hasAttachment(), msg='Workitem has attachments, but should not')

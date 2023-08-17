from enum import Enum
from .factory import createFromUri
import os
import requests


class Record(object):
    """
    Create a Polarion test record,

    :param polarion: Polarion client object
    :param test_run: Test run instance
    :param polarion_record: The data from Polarion of this testrun
    :param index: The index of this record in the test run

    """
    class ResultType(Enum):
        """
        Record result enum
        """
        No = None
        PASSED = 'passed'
        FAILED = 'failed'
        BLOCKED = 'blocked'
        NOTTESTED = 'not_tested'

    def __init__(self, polarion, test_run, polarion_record, index):
        self._polarion = polarion
        self._test_run = test_run
        self._polarion_record = polarion_record
        self._index = index

        self._postpone_save = False

        self._buildWorkitemFromPolarion()

    def __enter__(self):
        self._postpone_save = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._postpone_save = False
        self.save()

    def _buildWorkitemFromPolarion(self):
        # parse all polarion attributes to this class
        for attr, value in self._polarion_record.__dict__.items():
            for key in value:
                setattr(self, key, value[key])

        self._testcase = self._polarion_record.testCaseURI
        self._testcase_name = self._testcase.split('}')[1]
        self._defect = self._polarion_record.defectURI

    def _reloadFromPolarion(self):
        service = self._polarion.getService('TestManagement')
        self._polarion_record = service.getTestCaseRecords(self._test_run.uri, self._testcase)[0]
        self._buildWorkitemFromPolarion()
        # self._original_polarion_test_run = copy.deepcopy(self._polarion_test_run)

    def setTestStepResult(self, step_number, result: ResultType, comment=None):
        """"
        Set the result of a test step

        :param step_number: Step number
        :param result: The result fo the test step
        :param comment: An optional comment
        """
        if self.testStepResults is None:
            # get the number of test steps in
            service = self._polarion.getService('TestManagement')
            test_steps = service.getTestSteps(self.testCaseURI)
            number_of_steps = 0
            if test_steps.steps is not None:
                number_of_steps = len(test_steps.steps.TestStep)
            self.testStepResults = self._polarion.ArrayOfTestStepResultType()
            for _i in range(number_of_steps):
                self.testStepResults.TestStepResult.append(
                    self._polarion.TestStepResultType())

        if step_number < len(self.testStepResults.TestStepResult):
            self.testStepResults.TestStepResult[step_number].result = self._polarion.EnumOptionIdType(
                id=result.value)
            if comment is not None:
                self.testStepResults.TestStepResult[step_number].comment = self._polarion.TextType(
                    content=comment, type='text/html', contentLossy=False)

        self.save()

    def getResult(self):
        """
        Get the test result of this record

        :return: The test case result
        :rtype: ResultType
        """
        if self.result is not None:
            return self.ResultType(self.result.id)
        return self.ResultType.No

    def getComment(self):
        """
        Get a comment if available. The comment may contain HTML if edited in Polarion!

        :return: Get the comment, may contain HTML
        :rtype: string
        """
        if self.comment is not None:
            return self.comment.content
        return None

    @property
    def testcase_id(self):
        """
        The test case name including prefix
        """
        return self._testcase_name

    def getTestCaseName(self):
        """
        Get the test case name including prefix

        :return: The name
        :rtype: string
        """
        return self._testcase_name

    def setComment(self, comment):
        """
        tries to get the severity enum of this workitem type
        When it fails to get it, the list will be empty

        :param comment: Comment string, may contain HTML
        """
        self.comment = self._polarion.TextType(
            content=comment, type='text/html', contentLossy=False)

    def setResult(self, result: ResultType = ResultType.FAILED, comment=None):
        """
        Set the result of this record and save it.

        :param result: The result of this record
        :param comment: Comment string, may contain HTML
        """
        if comment is not None:
            self.setComment(comment)
        if self.result is not None:
            self.result.id = result.value
        else:
            self.result = self._polarion.EnumOptionIdType(
                id=result.value)
        self.save()

    def getExecutingUser(self):
        """
        Gets the executing user if the test was executed

        :return: The user
        :rtype: User/None
        """
        if self.executedByURI is not None:
            return createFromUri(self._polarion, None, self.executedByURI)
        return None

    def hasAttachment(self):
        """
        Checks if the Record has attachments

        :return: True/False
        :rtype: boolean
        """
        if self.attachments is not None:
            return True
        return False
    
    def getAttachment(self, file_name):
        """
        Get the attachment data

        :param file_name: The attachment file name
        :return: list of bytes
        :rtype: bytes[]
        """
        # find the file
        url = None
        for attachment in self.attachments.TestRunAttachment:
            if attachment.fileName == file_name:
                url = attachment.url

        if url is not None:
            return self._polarion.downloadFromSvn(url)
        else:
            raise Exception(f'Could not find attachment with name {file_name}')

    def saveAttachmentAsFile(self, file_name, file_path):
        """
        Save an attachment to file.

        :param file_name: The attachment file name
        :param file_path: File where to save the attachment
        """
        bin = self.getAttachment(file_name)
        with open(file_path, "wb") as file:
            file.write(bin)

    def deleteAttachment(self, file_name):
        """
        Delete an attachment.

        :param file_name: The attachment file name
        """
        service = self._polarion.getService('TestManagement')
        service.deleteAttachmentFromTestRecord(self._test_run.uri, self._index, file_name)
        self._reloadFromPolarion()

    def addAttachment(self, file_path, title):
        """
        Upload an attachment

        :param file_path: Source file to upload
        :param title: The title of the attachment
        """
        service = self._polarion.getService('TestManagement')
        file_name = os.path.split(file_path)[1]
        with open(file_path, "rb") as file_content:
            service.addAttachmentToTestRecord(self._test_run.uri, self._index, file_name, title, file_content.read())
        self._reloadFromPolarion()

    def testStepHasAttachment(self, step_index):
        """
        Checks if the a test step has attachments

        :param step_index: The test step index
        :return: True/False
        :rtype: boolean
        """
        if self.testStepResults is None:
            return False
        if self.testStepResults.TestStepResult[step_index].attachments is not None:
            return True
        return False
    
    def getAttachmentFromTestStep(self, step_index, file_name):
        """
        Get the attachment data from a test step

        :param step_index: The test step index
        :param file_name: The attachment file name
        :return: list of bytes
        :rtype: bytes[]
        """
        # find the file
        url = None
        for attachment in self.testStepResults.TestStepResult[step_index].attachments.TestRunAttachment:
            if attachment.fileName == file_name:
                url = attachment.url

        if url is not None:
            return self._polarion.downloadFromSvn(url)
        else:
            raise Exception(f'Could not find attachment with name {file_name}')

    def saveAttachmentFromTestStepAsFile(self, step_index, file_name, file_path):
        """
        Save an attachment to file from a test step

        :param step_index: The test step index
        :param file_name: The attachment file name
        :param file_path: File where to save the attachment
        """
        bin = self.getAttachmentFromTestStep(step_index, file_name)
        with open(file_path, "wb") as file:
            file.write(bin)

    def deleteAttachmentFromTestStep(self, step_index, file_name):
        """
        Delete an attachment from a test step

        :param step_index: The test step index
        :param file_name: The attachment file name
        """
        service = self._polarion.getService('TestManagement')
        service.deleteAttachmentFromTestStep(self._test_run.uri, self._index, step_index, file_name)
        self._reloadFromPolarion()

    def addAttachmentToTestStep(self, step_index, file_path, title):
        """
        Upload an attachment to a test step

        :param step_index: The test step index
        :param file_path: Source file to upload
        :param title: The title of the attachment
        """
        service = self._polarion.getService('TestManagement')
        file_name = os.path.split(file_path)[1]
        with open(file_path, "rb") as file_content:
            service.addAttachmentToTestStep(self._test_run.uri, self._index, step_index, file_name, title, file_content.read())
        self._reloadFromPolarion()

    def save(self):
        """
        Saves the current test record
        """
        if self._postpone_save:
            return

        new_item = {}
        for attr, value in self.__dict__.items():
            if not attr.startswith('_'):
                # only add if public value
                new_item[attr] = value
        service = self._polarion.getService('TestManagement')
        service.executeTest(
            self._test_run.uri, new_item)
        self._reloadFromPolarion()

    def __repr__(self):
        return f'{self._testcase_name} in {self._test_run.id} ({self.getResult()} on {self.executed})'

    def __str__(self):
        return f'{self._testcase_name} in {self._test_run.id} ({self.getResult()} on {self.executed})'

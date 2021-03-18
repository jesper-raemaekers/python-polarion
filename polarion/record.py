from enum import Enum
from collections import namedtuple
from .factory import createFromUri


class Record(object):
    """
    Create a Polarion test record,

    :param polarion: Polarion client object
    :param test_run: Test run instance
    :param polarion_record: The data from Polarion of this testrun

    """
    class ResultType(Enum):
        """
        Record result enum
        """
        No = None
        PASSED = 'passed'
        FAILED = 'failed'
        BLOCKED = 'blocked'

    def __init__(self, polarion, test_run, polarion_record):
        self._polarion = polarion
        self._test_run = test_run
        self._polarion_record = polarion_record

        # parse all polarion attributes to this class
        for attr, value in polarion_record.__dict__.items():
            for key in value:
                setattr(self, key, value[key])

        self._testcase = self._polarion_record.testCaseURI
        self._testcase_name = self._testcase.split('}')[1]
        self._defect = self._polarion_record.defectURI

    def setTestStepResult(self, step_number, result: ResultType, comment=None):
        """"
        Set the result of a test step

        :param step_number: Step number
        :param result: The result fo the test step
        :param comment: An optional comment
        """
        if self.testStepResults == None:
            # get the number of test steps in
            service = self._polarion.getService('TestManagement')
            test_steps = service.getTestSteps(self.testCaseURI)
            number_of_steps = 0
            if test_steps.steps != None:
                number_of_steps = len(test_steps.steps.TestStep)
            self.testStepResults = self._polarion.ArrayOfTestStepResultType()
            for _i in range(number_of_steps):
                self.testStepResults.TestStepResult.append(
                    self._polarion.TestStepResultType())

        if step_number < len(self.testStepResults.TestStepResult):
            self.testStepResults.TestStepResult[step_number].result = self._polarion.EnumOptionIdType(
                id=result.value)
            if comment != None:
                self.testStepResults.TestStepResult[step_number].comment = self._polarion.TextType(
                    content=comment, type='text/html', contentLossy=False)

        self.save()

    def getResult(self):
        """
        Get the test result of this record

        :return: The test case result
        :rtype: ResultType
        """
        if self.result != None:
            return self.ResultType(self.result.id)
        return self.ResultType.No

    def getComment(self):
        """
        Get a comment if available. The comment may contain HTML if edited in Polarion!

        :return: Get the comment, may contain HTML
        :rtype: string
        """
        if self.comment != None:
            return self.comment.content
        return None
    
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
        if comment != None:
            self.setComment(comment)
        if self.result != None:
            self.result.id = result.value
        else:
            self.result = self._polarion.EnumOptionIdType(
                id=result.value)
        self.save()

    def getExecutingUser(self):
        """
        Gets the executing user

        :return: The user
        :rtype: User
        """
        return createFromUri(self._polarion, None, self.executedByURI)

    def save(self):
        """
        Saves the current test record
        """
        new_item = {}
        for attr, value in self.__dict__.items():
            if attr.startswith('_') != True:
                # only add if public value
                new_item[attr] = value
        service = self._polarion.getService('TestManagement')
        service.executeTest(
            self._test_run.uri, new_item)

    def __repr__(self):
        return f'{self._testcase_name} in {self._test_run.id} ({self.getResult()} on {self.executed})'

    def __str__(self):
        return f'{self._testcase_name} in {self._test_run.id} ({self.getResult()} on {self.executed})'

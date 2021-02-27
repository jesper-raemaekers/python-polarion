from enum import Enum
# from .factory import createObjectFromUri


class Record(object):

    class ResultType(Enum):
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
        self._defect = self._polarion_record.defectURI

    def getResult(self):
        if self.result != None:
            return self.ResultType(self.result.id)
        return self.ResultType.No

    def getComment(self):
        """
        Get a comment if available. The comment may contain HTML if edited in Polarion!
        """
        if self.comment != None:
            return self.comment.content
        return None

    def setComment(self, comment):
        self.comment = {
            'type': 'text/html',
            'content': comment,
            'contentLossy': False
        }

    def setResult(self, result: ResultType = ResultType.FAILED, comment=None):
        if comment != None:
            self.setComment(comment)

        self.result = {}
        self.result['id'] = result.value
        self.save()

    def save(self):
        new_item = {}
        for attr, value in self.__dict__.items():
            if attr.startswith('_') != True:
                # only add if public value
                new_item[attr] = value
        service = self._polarion.getService('TestManagement')
        service.executeTest(
            self._test_run.uri, new_item)

    # def __repr__(self):
    #     return f'Record of {self.workitem.id} in run {self.test_run.id} {self.result}'

    # def __str__(self):
    #     return f'Record of {self.workitem.id} in run {self.test_run.id} {self.result}'

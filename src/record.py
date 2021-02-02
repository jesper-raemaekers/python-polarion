from .workitem import Workitem

class Record(object):

    def __init__(self, polarion, project, test_run, polarion_record):
        self.polarion = polarion
        self.project = project
        self.test_run = test_run
        self.polarion_record = polarion_record

        self.testcase = self.polarion_record.testCaseURI
        self.defect = self.polarion_record.defectURI

        self.result = self.polarion_record.result.id
        self.testStepResults = self.polarion_record.testStepResults

        try:
            self.workitem = Workitem(self.polarion, self.project, '', self.testcase)
        except:
            self.workitem = None

    def getTestcase(self):
        return self.workitem

    def getDefect(self):
        if self.defect:
            return Workitem(self.polarion, self.project, '', self.defect)

    def __repr__(self):
        return f'Record of {self.workitem.id} in run {self.test_run.id} {self.result}'

    def __str__(self):
        return f'Record of {self.workitem.id} in run {self.test_run.id} {self.result}'


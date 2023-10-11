import unittest

import zeep
from polarion.polarion import Polarion
from polarion.xml import Config, Importer, ResultExporter
from polarion.record import Record
#from keys import polarion_url, polarion_project_id, polarion_user, polarion_password, polarion_token
from keys import polarion_url, polarion_project_id, polarion_user, polarion_password

from unittest import mock

REQ_TYPE = 'requirement'
ISSUE_TYPE = 'issue'

class TestPolarionJunit(unittest.TestCase):

    def get_config (self, file):
        # return Config.from_dict({
        #     Config.XML_FILE: file,
        #     Config.URL: polarion_url,
        #     Config.USERNAME: polarion_user,
        #     Config.TOKEN: polarion_token,
        #     Config.PROJECT_ID: polarion_project_id,
        #     Config.TESTRUN_COMMENT: '',
        #     Config.USE_CACHE : True
        # })
        return Config.from_dict({
            Config.XML_FILE: file,
            Config.URL: polarion_url,
            Config.USERNAME: polarion_user,
            Config.PASSWORD: polarion_password,
            Config.PROJECT_ID: polarion_project_id,
            Config.TESTRUN_COMMENT: '',
            Config.USE_CACHE : True
        })

    def import_xml (self, file):
        return Importer.from_xml(self.get_config(file))

    def get_project(self):
        polarion=Polarion(polarion_url=polarion_url, user=polarion_user, password=polarion_password, cache=True)
        # polarion=Polarion(polarion_url=polarion_url, user=polarion_user, token=polarion_token, cache=True)
        project=polarion.getProject(polarion_project_id)
        return project

    def search_wi(self,project, wi):
        tmp = None
        try:
            tmp = project.getWorkitem(wi)
        except Exception:
            result = project.searchWorkitem(query=f'title:{wi}',field_list=['id','title'])
            if len(result) > 0 and result[0]['title'] == wi:
                tmp = project.getWorkitem(result[0]['id'])
        return tmp

    def create_wi (self, project, type, *wis):
        result = {}
        for wi in wis:
            tmp = self.search_wi(project, wi)
            if tmp is None:
                result[wi] = project.createWorkitem(type, wi)
            else:
                result[wi] = tmp
        return result

    def create_reqs (self, project, *reqs):
        return self.create_wi(project, REQ_TYPE, *reqs)

    def create_issue (self, project, *crs):
        return self.create_wi(project, ISSUE_TYPE, *crs)

    def test_import_xml_basic(self):
        testrun=self.import_xml('junit/no_properties.xml')
        self.assertIsNotNone(testrun)
        self.assertEqual(len(testrun.records),4)
        # impossible with the current api to map (without server calls) in the test to ID in the file
        nbFailed = 1
        nbBlocked = 1
        nbPassed = 1
        nbNotTested = 1
        for rec in testrun.records:
            if rec.getResult() == Record.ResultType.NOTTESTED:
                nbNotTested = nbNotTested - 1
            elif rec.getResult() == Record.ResultType.FAILED:
                nbFailed = nbFailed - 1
            elif rec.getResult() == Record.ResultType.PASSED:
                nbPassed = nbPassed - 1
            elif rec.getResult() == Record.ResultType.BLOCKED:
                nbBlocked = nbBlocked - 1
        self.assertEqual(nbFailed,0)
        self.assertEqual(nbPassed,0)
        self.assertEqual(nbNotTested,0)
        self.assertEqual(nbBlocked,0)
    
    def test_import_xml_properties(self):
        # create work items for testing purpose
        project = self.get_project()
        self.create_reqs(project, "REQ-001","REQ-002")
        self.create_issue(project, "ISSUE-001")

        testrun=self.import_xml('junit/properties.xml')
        self.assertIsNotNone(testrun)
        self.assertEqual(len(testrun.records),3)

        # verify REQ-001 traceability
        req001 = self.search_wi(project, "REQ-001")
        links = req001.getLinkedItemWithRoles()
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0][0],"verifies")
        self.assertEqual(links[0][1].title, "Tests.Registration.testCase8")

        # verify REQ-002 traceability
        req002 = self.search_wi(project, "REQ-002")
        links_req002=req002.getLinkedItemWithRoles()
        self.assertEqual(len(links_req002), 2)
        for link in links_req002:
            if link[0] == "verifies":
                self.assertEqual(link[1].title, "Tests.Registration.testCase8")
            elif link[0] == "relates_to":
                self.assertEqual(link[1].title, "Tests.Registration.testCase9")

        # verify ISSUE-001 traceability
        issue001 = self.search_wi(project, "ISSUE-001")
        links_issue = issue001.getLinkedItemWithRoles()
        self.assertEqual(len(links_issue), 1)
        self.assertEqual(links_issue[0][0],"verifies")
        self.assertEqual(links_issue[0][1].title, "Tests.Registration.testCase10")

    def test_import_xml_with_bad_link(self):
        testrun=self.import_xml('junit/properties-errors.xml')
        self.assertIsNotNone(testrun)
        self.assertEqual(len(testrun.records),1)

        project = self.get_project()
        req_does_not_exist =self.search_wi(project, "REQ-THAT-DOES-NOT-EXIST")
        self.assertIsNone(req_does_not_exist)

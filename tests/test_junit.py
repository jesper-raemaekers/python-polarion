import unittest

import zeep
from polarion.polarion import Polarion
from polarion.xml import Config, Importer, ResultExporter
from polarion.record import Record
from keys import polation_token, polarion_url, polarion_project_id, polarion_user

from unittest import mock


class TestPolarionJunit(unittest.TestCase):

    def test_import_xml(self):
        config=Config.from_dict({
            Config.XML_FILE: './tests/junit/no_properties.xml',
            Config.URL: polarion_url,
            Config.USERNAME: polarion_user,
            Config.PASSWORD: '',
            Config.TOKEN: polation_token,
            Config.PROJECT_ID: polarion_project_id,
            Config.TESTRUN_COMMENT: '',
            Config.USE_CACHE : True
        })

        testrun=Importer.from_xml(config)

        self.assertIsNotNone(testrun)
        self.assertEqual(len(testrun.records),4)
        # impossible with the current api to map easily in the test to ID in the file
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
import unittest
from polarion.polarion import Polarion
from polarion.project import Project
from .keys import polarion_user, polarion_password, polarion_url, polarion_project_id
from time import sleep
import mock


class TestPolarionWorkitem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pol = Polarion(
            polarion_url, polarion_user, polarion_password)
        cls.executing_project = cls.pol.getProject(
            polarion_project_id)

        cls.checking_project = cls.pol.getProject(
            polarion_project_id)

    def setUp(self):
        pass

    def test(self):
        pass

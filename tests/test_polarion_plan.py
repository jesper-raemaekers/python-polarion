import unittest
from polarion.polarion import Polarion
from datetime import date, datetime
from keys import polarion_user, polarion_password, polarion_url, polarion_project_id


class TestPolarionPlan(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pol = Polarion(
            polarion_url, polarion_user, polarion_password)
        cls.executing_project = cls.pol.getProject(
            polarion_project_id)
        cls.executing_plan = cls.executing_project.createPlan('Test plan' + datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f"),
                                                 datetime.now().strftime("%d-%m-%Y-%H-%M-%S-%f"), 'iteration')
            
    def setUp(self):
        pass

    def test_add_remove_workitem(self):
        workitem_package = self.executing_project.createWorkitem('workpackage')

        workitems_in_plan_start = self.executing_plan.getWorkitemsInPlan()
        self.executing_plan.addToPlan(workitem_package)
        workitems_in_plan_end = self.executing_plan.getWorkitemsInPlan()

        self.assertEqual(workitem_package.plannedInURIs.SubterraURI[0], self.executing_plan.uri, msg='Plan in workitem does not match current plan')
        self.assertEqual(len(workitems_in_plan_start) + 1, len(workitems_in_plan_end), msg='Workitems in plan did not increase by 1')

        workitems_in_plan_start = self.executing_plan.getWorkitemsInPlan()
        self.executing_plan.removeFromPlan(workitem_package)
        workitems_in_plan_end = self.executing_plan.getWorkitemsInPlan()

        self.assertIsNone(workitem_package.plannedInURIs, msg='Workitem still in plan')
        self.assertEqual(len(workitems_in_plan_start) - 1, len(workitems_in_plan_end),
                         msg='Workitems in plan did not decrease by 1')

    def test_add_remove_workitem_new_type(self):
        workitem_task = self.executing_project.createWorkitem('task')

        self.assertRaises(Exception, self.executing_plan, workitem_task, msg='No exception for unsupported type')

        self.executing_plan.addAllowedType(workitem_task.type.id)  

        self.assertEqual(self.executing_plan.allowedTypes.EnumOptionId[1].id, workitem_task.type.id, msg='workitem type not added')

        self.executing_plan.addToPlan(workitem_task)

        self.assertEqual(workitem_task.plannedInURIs.SubterraURI[0], self.executing_plan.uri, msg='Plan in workitem does not match current plan')

        self.executing_plan.removeFromPlan(workitem_task)

        self.assertIsNone(workitem_task.plannedInURIs, msg='Workitem still in plan')

        self.executing_plan.removeAllowedType(workitem_task.type.id)  

        self.assertEqual(len(self.executing_plan.allowedTypes.EnumOptionId), 1, msg='still more than one allowed type')

    def test_dates(self):
        due_date = date(2021, 1, 1)
        finished_on_date = datetime(2021, 1, 2)
        start_date = date(2021, 1, 3)
        started_on_date = datetime(2021, 1, 4)

        self.executing_plan.setDueDate(due_date)
        self.executing_plan.setFinishedOnDate(finished_on_date)
        self.executing_plan.setStartDate(start_date)
        self.executing_plan.setStartedOnDate(started_on_date)

        self.checking_plan = self.executing_project.getPlan(self.executing_plan.id)        

        self.assertEqual(self.executing_plan.dueDate.day, due_date.day, msg='Date is not equal')
        self.assertEqual(self.executing_plan.finishedOn.day, finished_on_date.day, msg='Date is not equal')
        self.assertEqual(self.executing_plan.startDate.day, start_date.day, msg='Date is not equal')
        self.assertEqual(self.executing_plan.startedOn.day, started_on_date.day, msg='Date is not equal')

        self.assertEqual(self.checking_plan.dueDate.day, due_date.day, msg='Date is not equal')
        self.assertEqual(self.checking_plan.finishedOn.day, finished_on_date.day, msg='Date is not equal')
        self.assertEqual(self.checking_plan.startDate.day, start_date.day, msg='Date is not equal')
        self.assertEqual(self.checking_plan.startedOn.day, started_on_date.day, msg='Date is not equal')










  
 
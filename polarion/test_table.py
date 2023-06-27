# coding=utf-8


class TestTable(object):
    """
    Uses a Test Workitem template to spawn a Test Table that can be used with the setTestSteps function.
    The constructor creates an empty table, and the methods in this class provide the means to construct a new
    TestSteps Table.
    :param test_template: Workitem to use as template for the new Test Table
    :type test_template: Workitem
    :param clear_table: Whether the test table is to be emptied after copy.
    :type clear_table: bool
    """

    def __init__(self, test_template: 'Workitem', clear_table=False):
        # get the custom fields
        raw_teststeps = test_template.getRawTestSteps()
        # Check if the template has the required columns
        if raw_teststeps is not None:
            if raw_teststeps.keys is not None and raw_teststeps.steps:
                self.columns = [col.id for col in raw_teststeps.keys.EnumOptionId]
            else:
                self.columns = test_template._getConfiguredTestStepColumnIDs()
        else:
            raise RuntimeError("This workitem doesn't have any Test Steps defined.")

        if clear_table or raw_teststeps.steps is None:
            self.steps = test_template._polarion.ArrayOfTestStepType()
        else:
            self.steps = raw_teststeps.steps
        self.step_type = test_template._polarion.TestStepType
        self.array_of_text_type = test_template._polarion.ArrayOfTextType
        self.array_of_test_step_type = test_template._polarion.ArrayOfTestStepType
        self.text_type = test_template._polarion.TextType

    def __len__(self):
        return len(self.steps.TestStep)

    def __getitem__(self, item):
        return self.steps.TestStep[item]

    def clear_teststeps(self):
        self.steps = self.array_of_test_step_type()

    def insert_teststep(self, position, *args):
        """
        Inserts a test step in the position indicated bu the `position` argument. The following parameters correspond to
         the columns that are required by the Test Workitem.
        :param position: Index where the step will be inserted. If the position is -1, then the step is appended.
        :type position: int
        :param *args: test columns that are expected by the Test Workitem.
        :type *args: list of strings
        :return: Nothing
        :rtype: None
        """
        if len(args) != len(self.columns):
            raise RuntimeError(f"The TestStep requires exactly {len(self.columns)} arguments.\n {self.columns}")

        step_values = self.array_of_text_type([self.text_type('text/html', str(args[i]), False) for i, col in enumerate(self.columns)])
        new_step = self.step_type(step_values)

        if position == -1:  # Needed to support append_teststep
            self.steps.TestStep.append(new_step)
        else:
            self.steps.TestStep.insert(position, new_step)

    def append_teststep(self, *args):
        self.insert_teststep(-1, *args)

    def delete_teststep(self, position):
        self.steps.TestStep.delete(position)

    def replace_teststep(self, position, *args):
        self.delete_teststep(position)
        self.insert_teststep(position, *args)
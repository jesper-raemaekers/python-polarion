# coding=utf-8
from polarion.base.custom_fields import PolarionWorkitemAttributeError


class TestIterator:

    def __init__(self, parent: 'TestTable', start=0, stop=None, increment=1):
        self.parent = parent
        self.counter = start
        if stop is None:
            self.stop = len(parent)
        else:
            self.stop = stop
        self.increment = increment

    def __iter__(self):
        self.counter = 0
        if self.stop is None:
            self.stop = len(self.parent)
        return self

    def __next__(self):
        if self.counter < self.stop:
            value = self.parent[self.counter]
            self.counter += self.increment
            return value
        else:
            raise StopIteration


class TestTable(object):
    """
    Uses a Test Workitem template to spawn a Test Table that can be used with the setTestSteps function.
    The constructor creates an empty table, and the methods in this class provide the means to construct a new
    TestSteps Table.
    :param test_template: Workitem to use as template for the new Test Table
    :type test_template: Workitem
    :param clear_table: Whether the test table is to be emptied after copy. This is useful when different test
                        templates exist.
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
            raise RuntimeError(f"Workitem {test_template.id} doesn't have any Test Steps defined.")

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

    def __getitem__(self, item) -> dict:
        current_row = {}
        for i, col_name in enumerate(self.columns):
            content = self.steps.TestStep[item].values.Text[i].content
            if content is None:
                current_row[col_name] = ''
            else:
                current_row[col_name] = content
        return current_row

    def __iter__(self):
        return TestIterator(parent=self)

    def getTestStep(self, position):
        return self.steps.TestStep[position]

    def clearTeststeps(self):
        """
        Removes all the test steps from the table.
        :return: Nothing
        """
        self.steps = self.array_of_test_step_type()

    def insertTestStep(self, position, *args):
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
            raise PolarionWorkitemAttributeError(f"Incorrect number of argument. Test step requires {len(self.columns)} arguments.\n {self.columns}")

        step_values = []
        for i, col in enumerate(self.columns):
            if args[i] is None:
                col_text = self.text_type('text/html', '', False)
            else:
                col_text = self.text_type('text/html', str(args[i]), False)
            step_values.append(col_text)

        step_values_array = self.array_of_text_type(step_values)
        new_step = self.step_type(step_values_array)

        if position == -1:  # Needed to support append_teststep
            self.steps.TestStep.append(new_step)
        else:
            self.steps.TestStep.insert(position, new_step)

    def addTestStep(self, *args):
        """
        Appends a test step at the end of the table. The following parameters correspond to the columns that are required
        by the Test Workitem.
        :param *args: test columns that are expected by the Test Workitem.
        :type *args: list of strings
        :return: Nothing
        """
        self.insertTestStep(-1, *args)

    def removeTestStep(self, position):
        """
        Removes a test step from the table.
        :param position: Index of the step to be removed.
        :type position: int
        :return: Nothing
        """
        if position >= len(self.steps.TestStep):
            raise ValueError(
                f'Index should be in range of test step length of {len(self.steps.TestStep)}'
                )
        self.steps.TestStep.pop(position)

    def updateTestStep(self, position, *args):
        """
        Replaces a test step in the table. The following parameters correspond to the columns that are required by the
        Test Workitem.
        :param position: Index of the step to be replaced.
        :type position: int
        :param *args: test columns that are expected by the Test Workitem.
        :type *args: list of strings
        :return: Nothing
        """
        self.removeTestStep(position)
        self.addTestStep(position, *args)

    # this is kept here for compatibility with the DM's repositories, which use python's standard naming convention
    insert_teststep = insertTestStep
    delete_teststep = removeTestStep
    replace_teststep = updateTestStep
    clear_teststeps = clearTeststeps
Polarion Test record
====================

Usage
--------------

Set the test case status:

.. code:: python

    # get a record from the test run
    test_record = test_run.records[0]
    #set status
    test_record.setResult(Record.ResultType.PASSED, 'some optional comment')

An exception is raised if the test run is not marked as automatic. Manual test cases require signing via Polarion web interface.

.. code::

    zeep.exceptions.Fault: java.lang.IllegalStateException: It is not allowed to sign on behalf of another user.


Set the status of an individual test case step:

.. code:: python

    # get a record from the test run
    test_record = test_run.records[0]
    #set status
    test_record.setTestStepResult(step_index, Record.ResultType.PASSED, 'See attachment')

Where step_index is a valid range for the current test case.

It is possible to use the context manager with a record.
This is useful, when updating all test steps in a record.
Execution speed increases, because the record is only updated once, when exiting the context manager.

.. code:: python

    with test_run.records[0] as test_record:
        for step_index in range(5):
            _record.setTestStepResult(step_index, Record.ResultType.PASSED, 'See attachment')


Attachments
--------------

To prove a test case, a attachment may be uploaded to test records and test case steps.  An example for the record attachments:

.. code:: python

    test_record = test_run.records[0]
    #upload a file
    test_record.addAttachment(path_to_file, 'file title')
    test_record.hasAttachment() # now true
    #download a file
    attachment_name = test_record.attachments.TestRunAttachment[0].fileName  
    test_record.saveAttachmentAsFile(attachment_name, path_to_new_file)
    #deleting attachment
    test_record.deleteAttachment(attachment_name)


.. note::
    Attachments to the record can only be uploaded if the record result has been set

An example for step attachments:

.. code:: python

    test_record = test_run.records[0]
    #upload a file
    test_record.addAttachmentToTestStep(step_index, path_to_file, 'file title')
    test_record.testStepHasAttachment(step_index) # now true
    #download a file
    attachment_name = test_record.testStepResults.TestStepResult[step_index].attachments.TestRunAttachment[0].fileName
    test_record.saveAttachmentFromTestStepAsFile(step_index, attachment_name, path_to_new_file)
    #deleting attachment
    test_record.deleteAttachmentFromTestStep(step_index, attachment_name)
    

.. note::
    Attachments to the test steps can only be uploaded if the test step result has been set.


List of available attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The attributes are set in the record when loading it from polarion. An attribute can be None (when it is not set), a string, number or datetime, or another object.
When accessing any attribute, a check for None is recommended.

Other attributes that will be available, but could be None, are listed below.


+----------------------------+---------------------------+-----------------------------------+------------------------------+
| Attribute                  | Type (when not None)      | getter                            | setter                       |
+============================+===========================+===================================+==============================+
| attachments                |                           | hasAttachment                     | deleteAttachment             |
|                            |                           |                                   |                              |
|                            |                           | saveAttachmentAsFile              | addAttachment                |
|                            |                           |                                   |                              |
|                            |                           | testStepHasAttachment             | updateAttachment             |
|                            |                           |                                   |                              |
|                            |                           | saveAttachmentFromTestStepAsFile  | deleteAttachmentFromTestStep |
|                            |                           |                                   |                              |
|                            |                           |                                   | addAttachmentToTestStep      |
|                            |                           |                                   |                              |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| comment                    |                           | getComment                        | setComment                   |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| defectURI                  |                           | No                                | No                           |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| duration                   |                           | No                                | No                           |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| executed                   |                           | No                                | No                           |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| executedByURI              |                           | getExecutingUser                  | No                           |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| iteration                  |                           | No                                | No                           |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| result                     |                           | getResult                         | setResult                    |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| signed                     |                           | No                                | No                           |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| testCaseRevision           |                           | No                                | No                           |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| testCaseURI                |                           | No                                | testcase_id                  |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| testParameters             |                           | No                                | No                           |
+----------------------------+---------------------------+-----------------------------------+------------------------------+
| testStepResults            |                           | No                                | setTestStepResult            |
+----------------------------+---------------------------+-----------------------------------+------------------------------+



Test record class
-----------------

.. autoclass:: polarion.record.Record
    :members:
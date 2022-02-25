Polarion Test runs
==================

Usage
--------------

The test run class provides access to the test records.

Currently the :attr:`~Testrun.records` holds the test records.

Creating a new test run using :class:`.Project` class

.. code:: python

    new_test_run = project.createTestRun('New-id', 'New test run title', 'template-id')

accessing an existing test run:

.. code:: python

    existing_test_run = self.checking_project.getTestRun('test-id')

adding a new test case to an existing test run:

.. code:: python

    test_case = project.getWorkitem('workitem-id')
    existing_test_run.addTestcase(test_case)

Set the test run status:

.. code:: python

    existing_test_run.status.id = 'verifiedPassed'
    existing_test_run.save()

.. note::
    There is currently no way to get the possible statuses for test run. Look in your Polarion config to find these values.


Attachments
--------------

A test run may have an attachment related to the test run. An example for working with attachments:

.. code:: python

    existing_test_run = self.checking_project.getTestRun('test-id')
    #upload a file
    existing_test_run.addAttachment(path_to_file, 'file title')
    existing_test_run.hasAttachment() # now true
    #download a file
    attachment_name = existing_test_run.attachments.TestRunAttachment[0].fileName  
    existing_test_run.saveAttachmentAsFile(attachment_name, path_to_new_file)
    #deleting attachment
    existing_test_run.deleteAttachment(attachment_name)


List of available attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The attributes are set in the test run when loading it from polarion. An attribute can be None (when it is not set), a string, number or datetime, or another object.
When accessing any attribute, a check for None is recommended as the only attributes that are always set are:
-Type
-Created
-ProjectUri


Other attributes that will be available, but could be None, are listed below.


+----------------------------+---------------------------+----------------------+-------------------------+
| Attribute                  | Type (when not None)      | getter               | setter                  |
+============================+===========================+======================+=========================+
| attachments                |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| authorURI                  |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| comments                   | object                    | No                   | addComment              |
+----------------------------+---------------------------+----------------------+-------------------------+
| created                    |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| customFields               |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| document                   |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| finishedOn                 |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| groupId                    |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| homePageContent            |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| id                         |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| idPrefix                   |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| isTemplate                 |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| keepInHistory              |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| location                   |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| projectSpanURIs            |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| projectURI                 |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| query                      |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| selectTestCasesBy          |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| status                     |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| summaryDefectURI           |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| templateURI                |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| testParameters             |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| title                      |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| type                       |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| unresolvable               |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| updated                    |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| uri                        |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| useReportFromTempla        |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+




Testrun class
--------------

.. autoclass:: polarion.testrun.Testrun
    :members:


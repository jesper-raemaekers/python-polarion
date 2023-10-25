Polarion xml importer
===================

Usage
--------------

This chapter details operations to import data.


Import an xml file of results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Import an xml file of results (see xml_junit.xsd for the standard format) into a new or an existing test run in a project
Import traceability to Workitems using their ids or their titles

.. code:: python

    import os
    from polarion.xml import Config, Importer, ResultExporter

    if __name__ == '__main__':
        import logging
        logging.basicConfig(level=logging.INFO)
        testrun_comment='comment to set in the test run' 

        config=Config.from_dict({
            Config.XML_FILE: 'xml_file.xml',
            Config.URL: 'http://hostname/polarion',
            Config.TOKEN: 'secret_token', # can also use USERNAME and PASSWORD
            Config.PROJECT_ID: 'project_id_in_polarion',
            Config.TESTRUN_ID: 'testrun_id_in_polarion', # if not set, create a new test run
            Config.TESTRUN_COMMENT: 'comment to add in the test run' # as an option.
            Config.USE_CACHE : 'True or False (Default) use the zeep cache' # as an option
            })

        testrun=Importer.from_xml(config)

        # if want to save the test_run as json, add:
        ResultExporter.save_json("result.json", testrun)

For traceability:

.. code-block:: XML

    <testcase name="testCase8" classname="Tests.Registration" assertions="4"
        time="1.625275" file="tests/registration.code" line="302">
        <!-- <properties> Some tools also support properties for test cases. -->
        <properties>
            <property name="verifies" value="REQ-001" />
            <property name="verifies" value="POLARION-ID" />
        </properties>
    </testcase>
    <testcase name="testCase10" classname="Tests.Registration" assertions="4">
        <system-out>
        [[PROPERTY|verifies=ISSUE-011]]
        </system-out>
    </testcase>

Export a test run as json
^^^^^^^^^^^^^^^^^^^^^^^^^

Can export a work item (tested for a test run) in json


.. code:: python

    from polarion.xml import ResultExporter

    ResultExporter.save_json('result.json', testrun)

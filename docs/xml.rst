Polarion xml importer
===================

Usage
--------------

This chapter details operations to import data.


Import an xml file of results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Import an xml file of results (see xml_junit.xsd for the standard format) into a new or an existing test run in a project


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
            })

        testrun=Importer.from_xml(config)

        # if want to save the test_run as json, add:
        ResultExporter.save_json("result.json", testrun)


Export a test run as json
^^^^^^^^^^^^^^^^^^^^^^^^^

Can export a work item (tested for a test run) in json


.. code:: python

    from polarion.xml import ResultExporter

    ResultExporter.save_json('result.json', testrun)

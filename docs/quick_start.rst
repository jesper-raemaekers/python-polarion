Quick start
===========

Creating the Polarion client:

.. code:: python

    from polarion.polarion import Polarion
    client = Polarion('http://example.com/polarion', 'user', 'password')


Opening a project using the project name:

.. code:: python

    project = client.getProject('Python')


Load a workitem:

.. code:: python

    workitem = project.getWorkitem('PYTH-510')

Modify a workitem:

.. code:: python
    
    x = workitem.getVailableActions() # x will be an array of actions
    workitem.preformAction(x[1])

or:

.. code:: python

    x = workitem.getVailableStatus() #this forces the new state ignoring any rules set in Polarion
    workitem.setStatus(x[1])

or:

.. code:: python

    workitem.setDescription('Some description..')
    workitem.addComment('test comment', 'sent from Python')
    workitem.addHyperlink('google.com', workitem.HyperlinkRoles.EXTERNAL_REF)

Getting options for this type of workitem:

.. code:: python

    workitem.getResolutionEnum() # these return an empty array of no workitem specific options are set
    workitem.getSeverityEnum()
    workitem.getStatusEnum()

You can modify any property and call the save method. Some require a certain structure, which methods like setDescription handle for you, not adhering to it will cause an exception.

Load a test run:

.. code:: python

    run = project.getTestRun('SWQ-0001')

or

.. code:: python

    runs = project.searchTestRuns('SWQ*') #this is a query and will work the same as in Polarion


Modifying a test record:

.. code:: python
    
    run = project.getTestRun('SWQ-0001')
    run.records[0].setResult(record.Record.ResultType.PASSED, ' Comment with test result')

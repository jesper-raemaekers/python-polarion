Polarion work items
===================

Usage
--------------

This chapter details some common operations

Updating a field
^^^^^^^^^^^^^^^^

The workitem can be updated and saved. The example below loads a workitem, changes the title and loads it again to show the changes have happened in Polarion.

.. code:: python

    workitem = project.getWorkitem('PYTH-510')
    print(f'Title: {workitem.title}')
    print(f'Status: {workitem.status.id}')
    print(f'Type: {workitem.type.id}')
    workitem.title = 'A custom new title!'
    workitem.save()

    reload_workitem = project.getWorkitem('PYTH-510')
    print(f'Title: {reload_workitem.title}')
    print(f'Status: {reload_workitem.status.id}')
    print(f'Type: {reload_workitem.type.id}')

Prints:

.. code:: python

    Title: title?
    Status: open
    Type: task
    Title: A custom new title!
    Status: open
    Type: task

Setting a new status
^^^^^^^^^^^^^^^^^^^^

Polarion status changes can be made by choosing one fo the available options for the workitem.

.. code:: python

    workitem = project.getWorkitem('PYTH-510')
    print(f'Status: {workitem.status.id}')
    actions = workitem.getAvailableActions()
    print(f' Actions: {actions}')

    workitem.preformAction(actions[0])

    reload_workitem = project.getWorkitem('PYTH-510')
    print(f'Status: {reload_workitem.status.id}')

prints:

.. code:: python

    Status: open
    Actions: ['start_progress', 'mark_done', 'mark_verified', 'reject']
    Status: inprogress

The rules set in Polarion apply to these actions. Failing to meet the rules will result in an exception:

.. code:: python

    Exception has occurred: Fault
    com.polarion.core.util.exceptions.UserFriendlyRuntimeException: 'Mark Done' failed for Work Item 'PYTH-510': The required field 'assignee' of Work Item 'PYTH-510' is empty

Workitem class
--------------

.. autoclass:: polarion.workitem.Workitem
    :members:
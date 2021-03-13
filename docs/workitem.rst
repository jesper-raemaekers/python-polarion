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

If a status requires other properties to be set, for example the resolution, then you can query options like so:

.. code:: python

    workitem = project.getWorkitem('PYTH-510')
    print(f'Status: {workitem.status.id}')
    actions = workitem.getAvailableActions()
    print(f' Actions: {actions}')
    resolutions = workitem.getResolutionEnum()
    project_resolutions = project.getEnum('resolution')
    print(f'Workitem resolutions: {resolutions}')
    print(f'Project resolutions: {project_resolutions}')

    workitem.setResolution(project_resolutions[11])
    workitem.preformAction(actions[1])

    reload_workitem = project.getWorkitem('PYTH-510')
    print(f'Status: {reload_workitem.status.id}')

Print:

.. code:: python

    Status: open
    Actions: ['start_progress', 'mark_done', 'mark_verified', 'reject']
    Workitem resolutions: []
    Project resolutions: ['done', 'valid', 'unsupported', 'wontdo', 'invalid', 'obsolete', 'duplicate', 'inactive', 'incomplete', 'other', 'cannotreproduce', 'later']
    Status: done

In this case not workitem specific resolutions are available (Polarion project setting) so only the project resolutions can be used.

.. warning::
    Currently there is no option available to check which resolutions are correct for the workflow defined in Polarion. You can set any resolution.

Changing the assignee
^^^^^^^^^^^^^^^^^^^^^

The assignee can be changed by getting a user from the project and setting it as assignee.

.. code:: python

    workitem = project.getWorkitem('PYTH-524')
    j = project.findUser('john')
    workitem.addAssignee(j)

Helpers
^^^^^^^

The workitem class implements the __eq__ method allowing it to be compared.

.. code:: python

    workitem1 = project.getWorkitem('PYTH-524')
    workitem2 = project.getWorkitem('PYTH-525')

    if workitem1 == workitem2:
    #...


List of available attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The attributes are set in the workitem when loading it from polarion. An attribute can be None (when it is not set), a string, number or datetime, or another object.
When accessing any attribute, a check for None is recommended as the only attributes that are always set are:
-Author
-Type
-Created

=====  =====
col 1  col 2
=====  =====
1      Second column of row 1.
2      Second column of row 2.
       Second line of paragraph.
3      - Second column of row 3.

       - Second item in bullet
         list (row 3, column 2).
\      Row 4; column 1 will be empty.
=====  =====

Other attributes that will be available, but could be None, are listed below.
Some objects only have one attribute, named id, these values can be accessed directly if not None. If they are None and you want to set them, use the setter method listed below.


+----------------------------+---------------------------+----------------------+-------------------------+
| Attribute                  | Type (when not None)      | getter               | setter                  |
+============================+===========================+======================+=========================+
| approvals                  |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| assignee                   | object                    | addAssignee          | getAssignedUsers        |
|                            |                           |                      |                         |
|                            |                           | removeAssignee       |                         |
+----------------------------+---------------------------+----------------------+-------------------------+
| attachments                |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| author                     | object                    | getAuthor            | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| categories                 |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| comments                   | object                    | No                   | addComment              |
+----------------------------+---------------------------+----------------------+-------------------------+
| created                    | datetime                  | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| customFields               |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| description                | object                    | getDescription       | setDescription          |
+----------------------------+---------------------------+----------------------+-------------------------+
| dueDate                    |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| externallyLinkedWorkItems  |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| hyperlinks                 |                           | No                   | addHyperlink            |
+----------------------------+---------------------------+----------------------+-------------------------+
| id                         | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| initialEstimate            | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| linkedOslcResources        |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| linkedRevisions            |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| linkedRevisionsDerived     |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| linkedWorkItems            |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| linkedWorkItemsDerived     |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| location                   | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| moduleURI                  |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| outlineNumber              |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| plannedEnd                 |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| plannedIn                  |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| plannedStart               |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| planningConstraints        |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| previousStatus             | object (id)               | No                   | No                      |
|                            |                           |                      |                         |
| previousStatus.id          | string                    |                      |                         |
+----------------------------+---------------------------+----------------------+-------------------------+
| priority                   | object (id)               | No                   | No                      |
|                            |                           |                      |                         |
| priority.id                | string                    |                      |                         |
+----------------------------+---------------------------+----------------------+-------------------------+
| project                    | object                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| remainingEstimate          | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| removeAssignee             |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| resolution                 | object (id)               | No                   | setResolution           |
|                            |                           |                      |                         |
| resolution.id              | string                    |                      |                         |
+----------------------------+---------------------------+----------------------+-------------------------+
| resolvedOn                 |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| severity                   | object (id)               | No                   | No                      |
|                            |                           |                      |                         |
| severity.id                | string                    |                      |                         |
+----------------------------+---------------------------+----------------------+-------------------------+
| status                     | object (id)               | No                   | preformAction           |
|                            |                           |                      |                         |
| status.id                  | string                    |                      | setStatus (not prefered)|
+----------------------------+---------------------------+----------------------+-------------------------+
| timePoint                  |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| timeSpent                  |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| title                      | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| type                       | object (id)               | No                   | No                      |
|                            |                           |                      |                         |
| type.id                    | string                    |                      |                         |
+----------------------------+---------------------------+----------------------+-------------------------+
| unresolvable               | boolean                   | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| updated                    | datetime                  | No                   |  No                     |
+----------------------------+---------------------------+----------------------+-------------------------+
| uri                        | string                    | No                   |  No                     |
+----------------------------+---------------------------+----------------------+-------------------------+
| workRecords                |                           | No                   |  No                     |
+----------------------------+---------------------------+----------------------+-------------------------+


Workitem class
--------------

.. autoclass:: polarion.workitem.Workitem
    :members:
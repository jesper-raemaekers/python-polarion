Polarion work items
===================

Usage
--------------

This chapter details some common operations.


Creating a new workitem
^^^^^^^^^^^^^^^^^^^^^^^

A new workitem can be created using :func:`~Project.createWorkitem`.

.. code:: python

    new_task = project.createWorkitem('changerequest')

    # Add fields to the creation. Needed if there are required fields upon creation.
    new_task = project.createWorkitem('task', new_workitem_fields={'title': 'New title'})

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

Prints::

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


Test case workitem
^^^^^^^^^^^^^^^^^^

Some workitems are test cases and can contain test steps. Use :func:`~Workitem.hasTestSteps` to determine if there are test steps.

A general example of working with test steps:

.. code:: python

    wi = prj.getWorkitem('PYTH-515')
    print(wi.getTestStepHeader())

    for i in range(3):
        wi.addTestStep(f'Step {i}', '', '')

    print(wi.getTestSteps())

    wi.removeTestStep(0)



Attachments
^^^^^^^^^^^^^^^^^^

A workitem  may have an attachment. An example for working with attachments:

.. code:: python

    workitem = project.getWorkitem('PYTH-524')
    #upload a file
    workitem.addAttachment(path_to_file, 'file title')
    workitem.hasAttachment() # now true
    #download a file
    attachment_id = workitem.attachments.TestRunAttachment[0].id  
    workitem.saveAttachmentAsFile(attachment_id, path_to_new_file)
    #update a file
    workitem.updateAttachment(attachment_id, path_to_file, 'file title')
    #deleting attachment
    workitem.deleteAttachment(attachment_id)

Linking
^^^^^^^

Workitems can be linked together using :func:`~Workitem.addLinkedItem`. In this example new_workitem_2 'relates to' new_workitem_1. new_workitem_1 will have the oppoite 'is related to' link.

.. code:: python

    new_workitem_2.addLinkedItem(new_workitem_1, 'relates_to')

Links can be retrieved either with or without link roles:

.. code:: python

    print(workitem_1.getLinkedItem()) # [PYTH-540: None]
    print(workitem_1.getLinkedItemWithRoles()) # [('follow_up', PYTH-540: None)]


Custom fields
^^^^^^^^^^^^^

If the workitem has any custom fields, they will be accessible via the customFields property. The method :func:`~Workitem.setCustomField` is available to set custom field values.
This method will create the custom field structure if not available.

.. code:: python

    workitem1.setCustomField('string_field', 'new string')
    workitem1.setCustomField('int_field', 99)
    workitem1.setCustomField('custom_enum_field', client.EnumOptionIdType(id='okay'))

Enums can be configured so that multiple options can be selected. This is not supported via the workitem class, but can be achieved manually.

.. code:: python

    enum_array = client.ArrayOfEnumOptionIdType()
    enum_array.EnumOptionId.append(client.EnumOptionIdType(id='open'))
    enum_array.EnumOptionId.append(client.EnumOptionIdType(id='done'))
    workitem1.setCustomField('multi_enum_field', enum_array)

Disabled features in Polarion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It has been reported that the addComment function can be disabled in Polarion. An exception will be thrown if this is the case in a specific Polarion instance. 

Helpers
^^^^^^^

The workitem class implements the __eq__ method allowing it to be compared.

.. code:: python

    workitem1 = project.getWorkitem('PYTH-524')
    workitem2 = project.getWorkitem('PYTH-525')

    if workitem1 == workitem2:
    #...

Context Manager
^^^^^^^^^^^^^^^

It is possible to use the context manager with a workitem.
This is useful, when updating many attributes of it.
Execution speed increases, because the workitem is only updated / saved once, when exiting the context manager.

.. code:: python

    with workitem as wi:
        wi.addAttachment(path_to_file, 'file title')
        wi.addComment('comment')
        # any many more


List of available attributes
----------------------------

The attributes are set in the workitem when loading it from polarion. An attribute can be None (when it is not set), a string, number or datetime, or another object.
When accessing any attribute, a check for None is recommended as the only attributes that are always set are:
-Author
-Type
-Created
-Project


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
| customFields               |                           | No                   | setCustomField          |
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
| linkedWorkItems            |                           | No                   | addLinkedItem           |
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

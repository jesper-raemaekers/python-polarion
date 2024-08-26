Project Group
=============

Initialization
--------------
The class can be instantiated like this:

.. code:: python

    pol = polarion.Polarion('http://example.com/polarion', 'user', 'password')
    project_group = pol.getProjectGroup('GroupName')


Methods
-------

.. automethod:: polarion.project_groups.ProjectGroup._find_group_recursive
.. automethod:: polarion.project_groups.ProjectGroup.searchWorkitem
.. automethod:: polarion.project_groups.ProjectGroup.getWorkitemsWithFields
.. automethod:: polarion.project_groups.ProjectGroup.getWorkitem


searchWorkitem
--------------
Search for workitems in the project group. To retrieve the workitems, use the `getWorkitemsWithFields` method.

.. code:: python

    project_group.searchWorkitem(query, order='Created', field_list=None, limit=-1)

Parameters:
- **query**: The query to search for
- **order**: The order of the results
- **field_list**: The list of fields to retrieve
- **limit**: The maximum number of results to retrieve


getWorkitemsWithFields
----------------------
Get the workitems in the project group. `field_list` acts as a filter to retrieve only the fields you need on the workitems you will get (default is all fields).

.. code:: python

    project_group.getWorkitemsWithFields(query='', order='Created', field_list=None, limit=-1)

Parameters:
- **query**: The query to search for
- **order**: The order of the results
- **field_list**: The list of fields to retrieve
- **limit**: The maximum number of results to retrieve


getWorkitem
-----------
Get one workitem by its ID.

.. code:: python

    project_group.getWorkitem(id)

Parameters:
- **id**: The ID of the workitem
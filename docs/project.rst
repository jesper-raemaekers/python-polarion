Polarion project
================

Initialization
--------------
The class can be instantiated like this:

.. code:: python

    pol = polarion.Polarion('http://example.com/polarion', 'user', 'password')
    project = pol.getProject('Python')


Custom fields
-------------

When querying workitems using :func:`~Project.searchWorkitem` or :func:`~Project.searchWorkitemInBaseline` you can select what field to load using the  'field_list' paramater.
To select custom field using this list, use the following syntax: ´customFields.<key name>´.
The example loads the custom field 'int_field' and 'string_field'.

.. code:: python

    project.searchWorkitem('type:task', field_list=['id', 'author', 'customFields.int_field', 'customFields.string_field'])



Project class
--------------

.. autoclass:: polarion.project.Project
    :members:
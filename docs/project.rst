Polarion project
================

Initialization
--------------
The class can be instantiated like this:

.. code:: python

    pol = polarion.Polarion('http://example.com/polarion', 'user', 'password')
    project = pol.getProject('Python')



Project class
--------------

.. autoclass:: polarion.project.Project
    :members:
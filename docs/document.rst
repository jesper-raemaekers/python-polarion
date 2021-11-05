Polarion LiveDoc
================

Usage
--------------

This chapter details some common operations

Creating a document
^^^^^^^^^^^^^^^^^^^

.. code:: python
    document = project.createDocument('_default', 'A new document', 'The document title', ['task'], 'relates_to')

Work items in a document
^^^^^^^^^^^^^^^^^^^^^^^^

Work items in a Polarion document are organized as a tree. By getting the top level item, you can iterate through all items by traversing their children.

.. code:: python
    top_work_item = document.getTopLevelWorkitem()
    children = top_work_item.getChildren()
    for child in children:
        print(child)

As an alternative, you can just get all work items in a document and work with them as a list.

.. code:: python
    work_items = document.getWorkitems()
    for work_item in work_items:
        print(work_item)

Work items can be added to documents as children of .

.. code:: python
    work_item = project.createWorkItem('task')
    work_item.createInDocument(work_item, document.getTopLevelWorkitem().uri)

Document class
--------------

.. autoclass:: polarion.document.Document
    :members:
Polarion LiveDoc
================

Usage
-----

This chapter details some common operations on Polarion LiveDocs

Creating and accessing a document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Documents are located in spaces in Polarion. To create a document, a space needs to be indicated. Additionally, the list of item types and
the link role for structural relationships (usually 'relates_to') are needed. The example below creates a document and retrieves it again.

.. code:: python

    spaces = project.getDocumentSpaces()
    document = project.createDocument(spaces[0], 'A new document', 'The document title', ['task'], 'relates_to')
    document = project.getDocument(f'spaces[0]/{document.name}')

Document headings
^^^^^^^^^^^^^^^^^

Headings are used to group workitems in a document. Headings can be created as children of other headings or on the top level.

.. code:: python

    chapter_1 = document.addHeading('Chapter 1')
    document.addHeading('Chapter 1.1', chapter_1)

Work items in a document
^^^^^^^^^^^^^^^^^^^^^^^^

Work items in a Polarion document are organized as a tree. By getting the top level item, you can iterate through all items by traversing their children in the document.
Additionally, you can get the parent of a workitem.

.. code:: python

    top_work_item = document.getTopLevelWorkitem()
    children = document.getChildren(top_work_item)
    for child in children:
        print(child)
        print(document.getParent(child))

As an alternative, you can just get all work items in a document and work with them as a list.

.. code:: python

    work_items = document.getWorkitems()
    for work_item in work_items:
        print(work_item)

Workitems can be added to documents as children of another workitem in the document.

.. code:: python

    work_item = project.createWorkItem('task')
    work_item.moveToDocument(work_item, document.getTopLevelWorkitem())

Reusing documents
^^^^^^^^^^^^^^^^^

It is possible to reuse documents with all contained workitems. The reused document can be updated to reflect the changes done in the original document.
In the following example, an existing document is reused, changed and the reused document is updated to the head revision.

.. code:: python

    reused_document = original_document.reuse(project.id, '_default', 'Reused document', 'derived_from')
    original_document.getTopLevelWorkitem().setDescription('Changed description')
    reused_document.update()

Document class
--------------

.. autoclass:: polarion.document.Document
    :members:
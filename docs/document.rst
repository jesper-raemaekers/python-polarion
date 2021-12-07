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

Custom fields
^^^^^^^^^^^^^

If the document has any custom fields, they will be accessible via the customFields property. The method :func:`~Document.setCustomField` is available to set custom field values.
This method will create the custom field structure if not available.

.. code:: python

    document.setCustomField('string_field', 'new string')
    document.setCustomField('int_field', 99)
    document.setCustomField('custom_enum_field', client.EnumOptionIdType(id='okay'))

Enums can be configured so that multiple options can be selected. This is not supported via the document class, but can be achieved manually.

.. code:: python

    enum_array = client.ArrayOfEnumOptionIdType()
    enum_array.EnumOptionId.append(client.EnumOptionIdType(id='open'))
    enum_array.EnumOptionId.append(client.EnumOptionIdType(id='done'))
    document.setCustomField('multi_enum_field', enum_array)

Note that Polarion does not support checking custom field availability for documents, so make sure that the document has the custom field configured before setting it.

Document class
--------------

.. autoclass:: polarion.document.Document
    :members:
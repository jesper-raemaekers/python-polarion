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

Workitems in a document
^^^^^^^^^^^^^^^^^^^^^^^^

Workitems in a Polarion document are organized as a tree. By getting the top level item, you can iterate through all items by traversing their children in the document.

.. code:: python

    top_work_item = document.getTopLevelWorkitem()
    children = document.getChildren(top_work_item)
    for child in children:
        print(child)

As an alternative, you can just get all workitems in a document and work with them as a list.

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

Comments
^^^^^^^^

You can add comments and replies to comments to a document.

.. code:: python

    comment = document.addComment('This is a document comment')
    document.addComment('And this is a reply', comment)

List of available attributes
----------------------------

The attributes are set in the document when loading it from polarion. An attribute can be None (when it is not set), a string, number or datetime, or another object.
When accessing any attribute, a check for None is recommended as the only attributes that are always set are:
-Author
-AutoSuspect
-Created
-Project
-StructureLinkRole
-UseOutlineNumbering

Other attributes that will be available, but could be None, are listed below.
Some objects only have one attribute, named id, these values can be accessed directly if not None. If they are None and you want to set them, use the setter method listed below.


+----------------------------+---------------------------+----------------------+-------------------------+
| Attribute                  | Type (when not None)      | getter               | setter                  |
+============================+===========================+======================+=========================+
| allowedWITypes             | object                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| areLinksFromParentToChild  | boolean                   | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| author                     | object                    | getAuthor            | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| autoSuspect                | boolean                   | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| branchedFrom               | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| branchedWithQuery          | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| comments                   | object                    | No                   | addComment              |
+----------------------------+---------------------------+----------------------+-------------------------+
| created                    | datetime                  | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| customFields               |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| derivedFields              |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| derivedFromLinkRole        |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| derivedFromURI             | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| headingSidebarField        | object                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| homePageContent            | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| id                         | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| linkedOslcResources        |                           | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| location                   | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| moduleAbsoluteLocation     | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| moduleFolder               | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| moduleLocation             | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| moduleName                 | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| project                    | object                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| status                     | object (id)               | No                   | No                      |
|                            |                           |                      |                         |
| status.id                  | string                    |                      |                         |
+----------------------------+---------------------------+----------------------+-------------------------+
| structureLinkRole          | object (id)               | No                   | No                      |
|                            |                           |                      |                         |
| structureLinkRole.id       | string                    |                      |                         |
+----------------------------+---------------------------+----------------------+-------------------------+
| title                      | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| type                       | object (id)               | No                   | No                      |
|                            |                           |                      |                         |
| type.id                    | string                    |                      |                         |
+----------------------------+---------------------------+----------------------+-------------------------+
| unresolvable               | boolean                   | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| updated                    | datetime                  | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| updatedBy                  | object                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| uri                        | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| useOutlineNumbering        | boolean                   | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+
| variantURI                 | string                    | No                   | No                      |
+----------------------------+---------------------------+----------------------+-------------------------+

Document class
--------------

.. autoclass:: polarion.document.Document
    :members:
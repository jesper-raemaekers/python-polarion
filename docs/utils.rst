Polarion Utils
================

Other useful functions that do not fit anywhere else.

HTML parsing
------------

You can get the parsed description by using the parser like the example below.
Passing the project to the parser is only needed when you want to find the title for linked workitems in the HTML text.
If not supplied it will only list the linked ID.

.. code:: python

    # if you have a project and workitem
    project = pol.getProject('')
    workitem = project.getWorkitem('')

    # get the parsed description like this
    parser = DescriptionParser(project)
    parser.feed(workitem.getDescription())
    print(parser.data)


Document functions
------------------

.. autofunction::polarion.utils.clean_html

.. autoclass:: polarion.utils.DescriptionParser
    :members:
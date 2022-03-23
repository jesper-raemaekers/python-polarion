Polarion Plans
==============

Creating a new plan
-----------------------

A new plan can be created using :func:`~Project.createPlan`. The template is project dependant, but default are 'iteration'
and 'release'.

.. code:: python

    project.createPlan('New iteration plan!', 'new-plan-1', 'iteration')
    project.createPlan('New release plan!', 'new-plan-2', 'release')


Usage
--------------

The plan class allows basic access to Plans in polarion. 


.. note::
    Note that for modifying plans you need the ALM license in Polarion.

You can get an existing plan or create a new one:

.. code:: python

    plan = project.getPlan('00002')


The template is project dependant, but default are 'iteration' and 'release'.

.. code:: python

    plan = project.createPlan('Test plan', '00002', 'iteration')
    plan = project.createPlan('Test plan', '00003', 'release')


In this test plan you can then add or remove workitems.

.. code:: python

    workitem = project.getWorkitem('xxx-000)
    plan.addToPlan(workitem)
    plan.removeFromPlan(workitem)


If the workitem type is not allowed in the plan, an exception will be raised.

You can however add or remove workitem types to the plan.

.. code:: python

    workitem = project.getWorkitem('xxx-000)
    plan.addAllowedType(workitem.type.id)
    plan.removeAllowedType(workitem.type.id)
    plan.addAllowedType('task')

A list of workitems in this plan can be retreived.

.. code:: python

    workitems = plan.getWorkitemsInPlan()

Plan class
----------

.. autoclass:: polarion.plan.Plan
    :members:


Polarion Plans
==============

Usage
--------------

The plan class allows basic access to Plans in polarion. 


.. note::
    Note that for modifying plans you need the ALM license in Polarion.

You can get an existing plan or create a new one:

.. code:: python

    plan = project.getPlan('00002')

.. code:: python

    plan = project.createPlan('Test plan', '00002', 'iteration')


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


Plan class
----------

.. autoclass:: polarion.plan.Plan
    :members:


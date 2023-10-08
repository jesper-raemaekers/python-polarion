# Python-polarion
[![Build status](https://dev.azure.com/jraemaekers/Python%20Polarion/_apis/build/status/Polarion-Python%20package-CI)](https://dev.azure.com/jraemaekers/Python%20Polarion/_build/latest?definitionId=5)
![Coverage](https://img.shields.io/azure-devops/coverage/jraemaekers/Python%20Polarion/5)
![Test](https://img.shields.io/azure-devops/tests/jraemaekers/Python%20Polarion/5)
[![Documentation Status](https://readthedocs.org/projects/python-polarion/badge/?version=latest)](https://python-polarion.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://pepy.tech/badge/polarion)](https://pepy.tech/project/polarion)


This package allows the user to access many Polarion items like workitems, test run, plans and documents.


# Feature overview

This package can, among others, read, modify and create:
- Workitems
- Test runs from templates
- Plans
- Documents

Work with attachments in workitems and test runs. 
Work with custom field in workitems and documents.

# Installation

```
pip install polarion
```

# Getting started

Creating the Polarion client and getting workitems, test runs or plans:

```python
from polarion import polarion
client = polarion.Polarion('http://example.com/polarion', 'user', 'password')
project = client.getProject('Python')
workitem = project.getWorkitem('PYTH-510')
run = project.getTestRun('SWQ-0001')
plan = project.getPlan('00002')
```

Modifying workitems:

```python
workitem.setDescription('Some description..')
workitem.addComment('test comment', 'sent from Python')
workitem.addHyperlink('google.com', workitem.HyperlinkRoles.EXTERNAL_REF)
```

Or test run results:
```python
run = project.getTestRun('SWQ-0001')
run.records[0].setResult(record.Record.ResultType.PASSED, ' Comment with test result')
```

Adding workitems to a plan:
```python
plan.addToPlan(workitem)
plan.removeFromPlan(workitem)
```


More examples to be found in the quick start section of the documentation.
[Go to the documentation](https://python-polarion.readthedocs.io/)

# How does it work?

This project uses the SOAP API of Polarion. This API exposes most of the user interactions you can do with Polarion like creating or editing workitems, plans and test runs.
The API is divided in seven different services which you can find from your Polarion instance at the url http://domain.com/polarion/ws/services.
Each of the services provides a WSDL file detailing the available functions. (Also available form you local instance at http://domain.com/polarion/ws/services/TrackerWebService?wsdl)
For this project the TrackerWebService, PlanningWebService and TestManagementWebService are the most used ones.

In general the project attempts for the objects (like workitems) to behave like Python objects which you can modify and are saved in the background. 
Where the API provide operation to preform an action that API call is used, and the object is reloaded from polarion to reflect the changes locally.

The API does not allow access to the project administration.

# Dependencies 

The package uses; requests, urllib3 and zeep.

It is tested for Python version 3.7 through 3.12.
Python 3.6 support has been dropped in 1.3.0.

# Known issues or missing features
- No way of knowing the test run possible statuses.
- Deleting work items used in documents does not remove the reference from the document.


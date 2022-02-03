# python-polarion
[![Build status](https://dev.azure.com/jraemaekers/Python%20Polarion/_apis/build/status/Polarion-Python%20package-CI)](https://dev.azure.com/jraemaekers/Python%20Polarion/_build/latest?definitionId=5)
![Coverage](https://img.shields.io/azure-devops/coverage/jraemaekers/Python%20Polarion/5)
![Test](https://img.shields.io/azure-devops/tests/jraemaekers/Python%20Polarion/5)
[![Documentation Status](https://readthedocs.org/projects/python-polarion/badge/?version=latest)](https://python-polarion.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://pepy.tech/badge/polarion)](https://pepy.tech/project/polarion)



This package allows access to a Polarion server.

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

# Known issues or missing features
- No way of knowing the test run possible statuses.


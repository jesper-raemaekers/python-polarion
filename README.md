# python-polarion
[![Build status](https://dev.azure.com/jraemaekers/Python%20Polarion/_apis/build/status/Python-Polarion%20branch)](https://dev.azure.com/jraemaekers/Python%20Polarion/_build/latest?definitionId=2)
![Coverage](https://img.shields.io/azure-devops/coverage/jraemaekers/Python%20Polarion/2)
![Test](https://img.shields.io/azure-devops/tests/jraemaekers/Python%20Polarion/2)
[![Documentation Status](https://readthedocs.org/projects/python-polarion/badge/?version=latest)](https://python-polarion.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://pepy.tech/badge/polarion)](https://pepy.tech/project/polarion)



This package allows access to a Polarion server.
Note that this is the first release and that updates will change the interface in the near future.

# Installation

```
pip install polarion
```

# Getting started

Creating the Polarion client and getting workitems or test runs:

```python
from polarion import polarion
client = polarion.Polarion('http://example.com/polarion', 'user', 'password')
project = client.getProject('Python')
workitem = project.getWorkitem('PYTH-510')
run = project.getTestRun('SWQ-0001')
```


More examples to be found in the quick start section of the documentation.
[Go to the documentation](https://python-polarion.readthedocs.io/)

# Known issues or missing features
- No way of knowing the test run possible statuses.
- No access to the live docs


